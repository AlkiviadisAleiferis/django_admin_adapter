from dateutil.relativedelta import relativedelta

from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework import status
from decimal import Decimal

from admin_api.model_admins import AgreementAdmin
from backend.tests.factories import (
    AgreementFactory,
    ContactFactory,
    UserFactory,
    ProjectFactory,
    PropertyFactory,
)
from backend.real_estate.models import Agreement, AgreementCommission
from backend.organization.models import User
from ..utils.create import (
    get_create_agreement_response,
)


# ----------- Test Permissions and errors


def test_object_create__only_post_and_get_allowed(staff_client, db):
    for method in ["put", "patch", "delete"]:
        resp = getattr(staff_client, method)("/api/real_estate/agreement/")
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_object_create__base_permission_check(non_staff_client, db, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    resp = get_create_agreement_response(non_staff_client)
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_object_create__base_admin_apiview_errors(staff_client, db):
    # Non-existent app
    resp = staff_client.post("/api/notanapp/agreement/", data={})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Non-existent model (real_estate app exists)
    resp = staff_client.post("/api/real_estate/notamodel/", data={})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Model exists but no admin registered
    resp = staff_client.post("/api/common/country/", data={})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}


def test_object_create__add_permission_required(db, no_perms_staff_client):
    # No permission
    resp = get_create_agreement_response(no_perms_staff_client)
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With add permission
    add_perm = Permission.objects.get(codename="add_agreement")

    no_perms_staff_client.user.user_permissions.set([add_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = get_create_agreement_response(
        no_perms_staff_client, data=dict(description="Test agreement description")
    )
    assert resp.status_code == status.HTTP_201_CREATED

    # Verify object was created
    assert Agreement.objects.filter(description="Test agreement description").exists()


# ----------- Test success cases no-inlines


def test_object_create__successful_creation(db, staff_client):
    initial_count = Agreement.objects.count()

    resp = get_create_agreement_response(
        staff_client,
        data={
            "type": Agreement.TypeChoices.CONTRACT_OF_SALE,
            "status": Agreement.StatusChoices.OPEN,
            "description": "New agreement",
            "price": "5000.00",
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED

    assert Agreement.objects.count() == initial_count + 1
    new_agreement = Agreement.objects.get(pk=resp.data["object"]["pk"])

    # Check response structure
    assert resp.data == {
        "messages": [f"New object {new_agreement} created successfully."],
        "object": {"pk": new_agreement.pk, "str": str(new_agreement)},
    }

    assert new_agreement.description == "New agreement"
    assert new_agreement.price == Decimal("5000.00")
    assert new_agreement.type == Agreement.TypeChoices.CONTRACT_OF_SALE
    assert new_agreement.status == Agreement.StatusChoices.OPEN


def test_object_create__creates_log_entry(db, staff_client):
    content_type = ContentType.objects.get_for_model(Agreement)

    # Count log entries before creation
    log_count_before = LogEntry.objects.filter(
        content_type=content_type,
        action_flag=ADDITION,
    ).count()

    resp = get_create_agreement_response(staff_client)
    assert resp.status_code == status.HTTP_201_CREATED

    # Check that a log entry was created
    log_entries = LogEntry.objects.filter(
        content_type=content_type,
        action_flag=ADDITION,
    )

    assert log_entries.count() == log_count_before + 1

    # Get the latest log entry
    log_entry = log_entries.order_by("-action_time").first()
    assert log_entry.user == staff_client.user
    assert log_entry.action_flag == ADDITION
    assert str(resp.data["object"]["pk"]) == log_entry.object_id


def test_object_create__with_related_fields(db, staff_client):
    project = ProjectFactory.create()
    property_obj = PropertyFactory.create()
    user = UserFactory.create()

    resp = get_create_agreement_response(
        staff_client,
        data={
            "type": Agreement.TypeChoices.CONTRACT_OF_SALE,
            "status": Agreement.StatusChoices.OPEN,
            "project": str(project.pk),
            "property": str(property_obj.pk),
            "assigned_to": str(user.pk),
            "description": "Agreement with relations",
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED

    new_agreement = Agreement.objects.get(pk=resp.data["object"]["pk"])
    assert new_agreement.project == project
    assert new_agreement.property == property_obj
    assert new_agreement.assigned_to == user
    assert new_agreement.description == "Agreement with relations"


# ----------- Test success cases with-inlines


def test_object_create__with_inline_formsets(db, staff_client):
    contact1 = ContactFactory.create(company=True)
    contact2 = ContactFactory.create(company=True)

    resp = get_create_agreement_response(
        staff_client,
        data={
            "type": Agreement.TypeChoices.CONTRACT_OF_SALE,
            "status": Agreement.StatusChoices.OPEN,
            "description": "Agreement with commissions",
        },
        commissions_data={
            "commissions-TOTAL_FORMS": "2",
            "commissions-INITIAL_FORMS": "0",
            "commissions-MIN_NUM_FORMS": "0",
            "commissions-MAX_NUM_FORMS": "0",
            "commissions-0-id": "",
            "commissions-0-beneficiary": str(contact1.pk),
            "commissions-0-value": "100.00",
            "commissions-1-id": "",
            "commissions-1-beneficiary": str(contact2.pk),
            "commissions-1-value": "200.00",
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED

    # Verify agreement was created
    new_agreement = Agreement.objects.get(pk=resp.data["object"]["pk"])
    assert new_agreement.description == "Agreement with commissions"

    # Verify commissions were created
    commissions = new_agreement.commissions.all().order_by("value")
    assert commissions.count() == 2
    assert commissions[0].beneficiary == contact1
    assert commissions[0].value == Decimal("100.00")
    assert commissions[1].beneficiary == contact2
    assert commissions[1].value == Decimal("200.00")


# ----------- Test Validation errors


def test_object_create__form_field_and_non_field_errors(db, staff_client):
    # Send invalid data (missing required fields)
    resp = get_create_agreement_response(
        staff_client,
        data={
            "type": "",  # Required field
            "status": "",  # Required field
            "description": "Invalid agreement",
            "valid_until": "2025-12-08",
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # Check error structure
    assert resp.data == {
        "error_data": {
            "type": [{"message": "This field is required.", "code": "required"}],
            "status": [{"message": "This field is required.", "code": "required"}],
            "valid_until": [
                {
                    "message": "Valid until cannot be set if valid form is null.",
                    "code": "",
                }
            ],
        },
        "inlines_error_data": {
            "commissions": {"forms_errors": [{}], "non_forms_errors": []}
        },
    }


def test_object_create__inline_formset_all_error_types(db, staff_client):
    contact1 = ContactFactory.create(company=True)
    contact2 = ContactFactory.create(person=True)

    # Create with invalid inline formset data
    commissions_data = {
        # Inline formset management form
        "commissions-TOTAL_FORMS": "2",
        "commissions-INITIAL_FORMS": "0",
        "commissions-MIN_NUM_FORMS": "0",
        "commissions-MAX_NUM_FORMS": "1000",
        # valid! will have an empty dict on errors list
        "commissions-0-id": "",
        "commissions-0-beneficiary": contact1.id,  # Required field
        "commissions-0-value": "100.00",
        "commissions-0-DELETE": "",
        # Invalid commission (must be a company but is person)
        "commissions-1-id": "",
        "commissions-1-beneficiary": contact2.id,  # invalid is a person
        "commissions-1-value": "-100.00",
        "commissions-1-DELETE": "",
    }

    resp = get_create_agreement_response(
        staff_client,
        data={
            "type": Agreement.TypeChoices.TENANCY_AGREEMENT,
            "status": Agreement.StatusChoices.OPEN,
            "description": "Invalid agreement",
            "valid_from": "2025-12-08",
            "valid_until": "2025-12-09",
        },
        commissions_data=commissions_data,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # Check error structure
    assert resp.data == {
        "error_data": {},
        "inlines_error_data": {
            "commissions": {
                "forms_errors": [
                    {},
                    {
                        "value": ["This value must be positive."],
                        "__all__": ["Beneficiary must be a company."],
                    },
                ],
                "non_forms_errors": [
                    {
                        "message": "Only a Contract of Sale Agreement can have beneficiaries.",
                        "code": "",
                    }
                ],
            }
        },
    }


def test_object_create__all_possible_error_types(db, staff_client):
    tommorow = timezone.localdate() + relativedelta(days=1)
    contact1 = ContactFactory.create(company=True)
    contact2 = ContactFactory.create(person=True)

    # Create with invalid inline formset data
    commissions_data = {
        # Inline formset management form
        "commissions-TOTAL_FORMS": "2",
        "commissions-INITIAL_FORMS": "0",
        "commissions-MIN_NUM_FORMS": "0",
        "commissions-MAX_NUM_FORMS": "1000",
        # valid! will have an empty dict on errors list
        "commissions-0-id": "",
        "commissions-0-beneficiary": contact1.id,  # Required field
        "commissions-0-value": "100.00",
        "commissions-0-DELETE": "",
        # Invalid commission (must be a company but is person)
        "commissions-1-id": "",
        "commissions-1-beneficiary": contact2.id,  # invalid is a person
        "commissions-1-value": "-100.00",
        "commissions-1-DELETE": "",
    }

    resp = get_create_agreement_response(
        staff_client,
        data={
            "type": Agreement.TypeChoices.TENANCY_AGREEMENT,
            "status": Agreement.StatusChoices.OPEN,
            "description": "Invalid agreement",
            "reservation_date": "asd",  # wrong date format -> field error
            "valid_from": tommorow.strftime("%Y-%m-%d"),
            "valid_until": timezone.localdate().strftime("%Y-%m-%d"),
        },
        commissions_data=commissions_data,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # Check error structure
    assert resp.data == {
        "error_data": {
            "reservation_date": [{"message": "Enter a valid date.", "code": "invalid"}],
            "__all__": [
                {"message": "Valid until cannot be before valid from.", "code": ""}
            ],
        },
        "inlines_error_data": {
            "commissions": {
                "forms_errors": [
                    {},
                    {
                        "value": ["This value must be positive."],
                        "__all__": ["Beneficiary must be a company."],
                    },
                ],
                "non_forms_errors": [
                    {
                        "message": "Only a Contract of Sale Agreement can have beneficiaries.",
                        "code": "",
                    }
                ],
            }
        },
    }


# ----------- Other


def test_object_create__all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement_has_add_permission_spy = mocker.spy(AgreementAdmin, "has_add_permission")
    agreement_get_fieldsets_spy = mocker.spy(AgreementAdmin, "get_fieldsets")
    agreement_get_form_spy = mocker.spy(AgreementAdmin, "get_form")
    agreement_create_formsets_spy = mocker.spy(AgreementAdmin, "_create_formsets")
    agreement_save_form_spy = mocker.spy(AgreementAdmin, "save_form")
    agreement_save_model_spy = mocker.spy(AgreementAdmin, "save_model")
    agreement_save_related_spy = mocker.spy(AgreementAdmin, "save_related")
    agreement_construct_change_message_spy = mocker.spy(
        AgreementAdmin, "construct_change_message"
    )
    agreement_log_addition_spy = mocker.spy(AgreementAdmin, "log_addition")

    resp = get_create_agreement_response(staff_client)
    assert resp.status_code == status.HTTP_201_CREATED

    admin_site_has_permission_spy.assert_called()
    agreement_has_add_permission_spy.assert_called()
    agreement_get_fieldsets_spy.assert_called()
    agreement_get_form_spy.assert_called()
    agreement_create_formsets_spy.assert_called()
    agreement_save_form_spy.assert_called()
    agreement_save_model_spy.assert_called()
    agreement_save_related_spy.assert_called()
    agreement_construct_change_message_spy.assert_called()
    agreement_log_addition_spy.assert_called()


def test_object_create__multiple_creations(db, staff_client):
    initial_count = Agreement.objects.count()

    # First creation
    resp1 = get_create_agreement_response(
        staff_client,
        data={
            "type": Agreement.TypeChoices.CONTRACT_OF_SALE,
            "status": Agreement.StatusChoices.OPEN,
            "description": "First agreement",
        },
    )
    assert resp1.status_code == status.HTTP_201_CREATED

    # Second creation
    resp2 = get_create_agreement_response(
        staff_client,
        data={
            "type": Agreement.TypeChoices.CONTRACT_OF_SALE,
            "status": Agreement.StatusChoices.OPEN,
            "description": "Second agreement",
        },
    )
    assert resp2.status_code == status.HTTP_201_CREATED

    # Verify both were created
    assert Agreement.objects.count() == initial_count + 2

    # Verify they have different PKs
    assert resp1.data["object"]["pk"] != resp2.data["object"]["pk"]

    # Verify data
    agreement1 = Agreement.objects.get(pk=resp1.data["object"]["pk"])
    agreement2 = Agreement.objects.get(pk=resp2.data["object"]["pk"])

    assert agreement1.description == "First agreement"
    assert agreement1.type == Agreement.TypeChoices.CONTRACT_OF_SALE
    assert agreement2.description == "Second agreement"
    assert agreement2.type == Agreement.TypeChoices.CONTRACT_OF_SALE


def test_object_create__view_permission_not_sufficient(db, no_perms_staff_client):
    # With only view permission
    view_perm = Permission.objects.get(codename="view_agreement")

    no_perms_staff_client.user.user_permissions.set([view_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = get_create_agreement_response(no_perms_staff_client)
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify object was NOT created
    assert not Agreement.objects.filter(description="Test agreement description").exists()


def test_object_create__change_permission_not_sufficient(db, no_perms_staff_client):
    # With only change permission
    change_perm = Permission.objects.get(codename="change_agreement")
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = get_create_agreement_response(no_perms_staff_client)
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify object was NOT created
    assert not Agreement.objects.filter(description="Test agreement description").exists()


def test_object_create__delete_permission_not_sufficient(db, no_perms_staff_client):
    # With only delete permission
    delete_perm = Permission.objects.get(codename="delete_agreement")
    no_perms_staff_client.user.user_permissions.set([delete_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = get_create_agreement_response(no_perms_staff_client)
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify object was NOT created
    assert not Agreement.objects.filter(description="Test agreement description").exists()


def test_object_create__inline_permissions_required(db, no_perms_staff_client):
    contact = ContactFactory.create()

    # With add permission for agreement but not for commissions
    add_perm = Permission.objects.get(codename="add_agreement")

    no_perms_staff_client.user.user_permissions.set([add_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    # Try to create with inline data
    commissions_data = {
        "commissions-TOTAL_FORMS": "1",
        "commissions-INITIAL_FORMS": "0",
        "commissions-MIN_NUM_FORMS": "0",
        "commissions-MAX_NUM_FORMS": "1000",
        "commissions-0-id": "",
        "commissions-0-beneficiary": str(contact.pk),
        "commissions-0-value": "100.00",
        "commissions-0-DELETE": "",
    }

    resp = get_create_agreement_response(
        no_perms_staff_client, commissions_data=commissions_data
    )

    assert resp.status_code == status.HTTP_201_CREATED

    # Commission should not be created without permission
    # even if data is sent
    new_agreement = Agreement.objects.get(pk=resp.data["object"]["pk"])
    assert new_agreement.commissions.count() == 0
