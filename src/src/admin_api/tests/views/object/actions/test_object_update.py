import pytest
from dateutil.relativedelta import relativedelta
from datetime import date, time

from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.admin.models import LogEntry, CHANGE
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
from ..utils import get_update_agreement_response


# ----------- Test Permissions and errors


def test_object_update__only_put_allowed(staff_client, db):
    agreement = AgreementFactory.create()
    for method in ["post", "patch", "get"]:
        resp = getattr(staff_client, method)(
            f"/api/real_estate/agreement/{agreement.pk}/"
        )
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_object_update__base_permission_check(non_staff_client, db, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement = AgreementFactory.create()
    resp = non_staff_client.put(
        f"/api/real_estate/agreement/{agreement.pk}/",
        data={"description": "Updated"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_object_update__base_admin_apiview_errors(staff_client, db):
    # Non-existent app
    resp = staff_client.put("/api/notanapp/agreement/1/", data={})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Non-existent model (real_estate app exists)
    resp = staff_client.put("/api/real_estate/notamodel/1/", data={})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Model exists but no admin registered
    resp = staff_client.put("/api/common/country/1/", data={})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}


def test_object_update__change_permission_required(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    # No permission
    resp = get_update_agreement_response(
        agreement,
        no_perms_staff_client,
        {"description": "Updated description"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With change permission
    change_perm = Permission.objects.get(codename="change_agreement")
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = get_update_agreement_response(
        agreement,
        no_perms_staff_client,
        {"description": "Updated description"},
    )
    assert resp.status_code == status.HTTP_200_OK

    # Verify object was updated
    agreement.refresh_from_db()
    assert agreement.description == "Updated description"


def test_object_update__object_not_found(staff_client):
    resp = staff_client.put(
        "/api/real_estate/agreement/999999999999/",
        data={"description": "Updated"},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ----------- Test success cases no-inlines


def test_object_update__successful_update__no_inlines(db, no_perms_staff_client):
    agreement = AgreementFactory.create(
        description="Original description",
        price=Decimal("1000.00"),
    )

    # With change permission
    change_perm = Permission.objects.get(codename="change_agreement")
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = get_update_agreement_response(
        agreement,
        no_perms_staff_client,
        {
            "description": "Updated description",
            "price": 2000.00,
        },
    )
    assert resp.status_code == status.HTTP_200_OK

    # Check response structure
    assert resp.data == {"messages": [f"{agreement} updated successfully."]}

    # Verify object was actually updated in database
    agreement.refresh_from_db()
    assert agreement.description == "Updated description"
    assert agreement.price == Decimal("2000.00")


def test_object_update__partial_update_preserves_other_fields__no_inlines(
    db, no_perms_staff_client
):
    agreement = AgreementFactory.create(
        description="Original description",
        price=Decimal("1000.00"),
    )
    old_values = {
        "status": agreement.status,
        "agreement_signing_date": agreement.agreement_signing_date,
        "signing_time": agreement.signing_time,
        "assigned_to": agreement.assigned_to_id,
        "project": agreement.project_id,
        "property": agreement.property_id,
        "unique_id": agreement.unique_id,
        "website_url": agreement.website_url,
        "slug": agreement.slug,
        "closure_percentage": agreement.closure_percentage,
        "agreement_int": agreement.agreement_int,
        "description": agreement.description,
        "valid_from": agreement.valid_from,
        "valid_until": agreement.valid_until,
        "cancel_date": agreement.cancel_date,
        "reservation_date": agreement.reservation_date,
        "price": agreement.price,
        "down_payment": agreement.down_payment,
        "private_agreement_date": agreement.private_agreement_date,
    }

    # With change permission
    change_perm = Permission.objects.get(codename="change_agreement")
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = get_update_agreement_response(
        agreement,
        no_perms_staff_client,
        {
            "description": "Updated description",
            "price": 2000.00,
        },
    )
    assert resp.status_code == status.HTTP_200_OK

    # Check response structure
    assert resp.data == {"messages": [f"{agreement} updated successfully."]}

    agreement.refresh_from_db()
    assert agreement.description == "Updated description"
    assert agreement.price == Decimal("2000.00")
    #
    assert agreement.status == old_values["status"]
    assert agreement.agreement_signing_date == old_values["agreement_signing_date"]
    assert agreement.signing_time == old_values["signing_time"]
    assert agreement.assigned_to_id == old_values["assigned_to"]
    assert agreement.project_id == old_values["project"]
    assert agreement.property_id == old_values["property"]
    assert agreement.unique_id == old_values["unique_id"]
    assert agreement.website_url == old_values["website_url"]
    assert agreement.slug == old_values["slug"]
    assert agreement.closure_percentage == old_values["closure_percentage"]
    assert agreement.agreement_int == old_values["agreement_int"]
    assert agreement.valid_from == old_values["valid_from"]
    assert agreement.valid_until == old_values["valid_until"]
    assert agreement.cancel_date == old_values["cancel_date"]
    assert agreement.reservation_date == old_values["reservation_date"]
    assert agreement.down_payment == old_values["down_payment"]
    assert agreement.private_agreement_date == old_values["private_agreement_date"]


def test_object_update__update_all_fields__no_inlines(db, no_perms_staff_client):
    agreement = AgreementFactory.create(
        type=Agreement.TypeChoices.TENANCY_AGREEMENT,
        status=Agreement.StatusChoices.OPEN,
        description="Description",
        agreement_signing_date=None,
        signing_time=None,
        assigned_to=None,
        project=None,
        property=None,
        unique_id=None,
        website_url=None,
        slug=None,
        closure_percentage=None,
        agreement_int=None,
        valid_from=None,
        valid_until=None,
        cancel_date=None,
        reservation_date=None,
        price=None,
        down_payment=None,
        private_agreement_date=None,
    )
    old_values = {
        "status": agreement.status,
        "description": agreement.description,
        "agreement_signing_date": agreement.agreement_signing_date,
        "signing_time": agreement.signing_time,
        "assigned_to": agreement.assigned_to_id,
        "project": agreement.project_id,
        "property": agreement.property_id,
        "unique_id": agreement.unique_id,
        "website_url": agreement.website_url,
        "slug": agreement.slug,
        "closure_percentage": agreement.closure_percentage,
        "agreement_int": agreement.agreement_int,
        "valid_from": agreement.valid_from,
        "valid_until": agreement.valid_until,
        "cancel_date": agreement.cancel_date,
        "reservation_date": agreement.reservation_date,
        "price": agreement.price,
        "down_payment": agreement.down_payment,
        "private_agreement_date": agreement.private_agreement_date,
    }
    new_values = {
        "status": Agreement.StatusChoices.RESERVED,
        "description": "Updated description",
        "agreement_signing_date": date(2025, 12, 4),
        "signing_time": time(16, 13, 10),
        "assigned_to": UserFactory().id,
        "project": ProjectFactory().id,
        "property": PropertyFactory().id,
        "unique_id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
        "website_url": "https://example.com",
        "slug": "agreement-slug",
        "closure_percentage": 0.2,
        "agreement_int": 22,
        "valid_from": date(2025, 12, 4),
        "valid_until": date(2025, 12, 6),
        "cancel_date": date(2025, 12, 5),
        "reservation_date": date(2025, 12, 2),
        "price": 2000.00,
        "down_payment": 200.00,
        "private_agreement_date": date(2025, 12, 3),
    }

    # With change permission
    change_perm = Permission.objects.get(codename="change_agreement")
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = get_update_agreement_response(
        agreement,
        no_perms_staff_client,
        new_values,
    )
    assert resp.status_code == status.HTTP_200_OK

    # Check response structure
    assert resp.data == {"messages": [f"{agreement} updated successfully."]}

    agreement.refresh_from_db()
    assert agreement.description == "Updated description"
    assert agreement.price == Decimal("2000.00")
    #
    assert agreement.status == new_values["status"]
    assert agreement.agreement_signing_date == new_values["agreement_signing_date"]
    assert agreement.signing_time == new_values["signing_time"]
    assert agreement.assigned_to_id == new_values["assigned_to"]
    assert agreement.project_id == new_values["project"]
    assert agreement.property_id == new_values["property"]
    assert str(agreement.unique_id) == new_values["unique_id"]
    assert agreement.website_url == new_values["website_url"]
    assert agreement.slug == new_values["slug"]
    assert agreement.closure_percentage == new_values["closure_percentage"]
    assert agreement.agreement_int == new_values["agreement_int"]
    assert agreement.valid_from == new_values["valid_from"]
    assert agreement.valid_until == new_values["valid_until"]
    assert agreement.cancel_date == new_values["cancel_date"]
    assert agreement.reservation_date == new_values["reservation_date"]
    assert agreement.down_payment == new_values["down_payment"]
    assert agreement.private_agreement_date == new_values["private_agreement_date"]
    for field in new_values:
        assert new_values[field] != old_values[field]


def test_object_update__creates_log_entry__no_inlines(db, no_perms_staff_client):
    agreement = AgreementFactory.create(description="Original")
    agreement_pk = agreement.pk
    content_type = ContentType.objects.get_for_model(agreement)

    # Ensure no log entries exist before update
    log_count_before = LogEntry.objects.filter(
        content_type=content_type,
        object_id=str(agreement_pk),
    ).count()

    # With change permission
    change_perm = Permission.objects.get(codename="change_agreement")
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = get_update_agreement_response(
        agreement,
        no_perms_staff_client,
        {
            "description": "Updated description",
        },
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {"messages": [f"{agreement} updated successfully."]}

    # Check that a log entry was created
    log_entries = LogEntry.objects.filter(
        content_type=content_type,
        object_id=str(agreement_pk),
        action_flag=CHANGE,
    )

    assert log_entries.count() == log_count_before + 1

    log_entry = log_entries.first()
    assert log_entry.user == no_perms_staff_client.user
    assert log_entry.action_flag == CHANGE


# ----------- Test success cases with-inlines


def test_object_update__update_delete_create_inline_objects(db, staff_client):
    agreement = AgreementFactory.create(type=Agreement.TypeChoices.CONTRACT_OF_SALE.value)
    contact1 = ContactFactory.create(company=True)
    contact2 = ContactFactory.create(company=True)
    contact3 = ContactFactory.create(company=True)

    # Create existing commission
    commission1 = AgreementCommission.objects.create(
        agreement=agreement, beneficiary=contact1, value=100.00
    )
    commission2 = AgreementCommission.objects.create(
        agreement=agreement, beneficiary=contact2, value=100.00
    )

    # Update with inline formset data
    resp = get_update_agreement_response(
        agreement,
        staff_client,
        data={
            "type": agreement.type,
            "status": agreement.status,
            "description": "Updated with inlines",
        },
        commissions_data={
            # Inline formset management form
            "commissions-TOTAL_FORMS": "3",
            "commissions-INITIAL_FORMS": "2",
            "commissions-MIN_NUM_FORMS": "0",
            "commissions-MAX_NUM_FORMS": "1000",
            # Update existing commission
            "commissions-0-id": commission1.pk,
            "commissions-0-beneficiary": contact1.pk,
            "commissions-0-value": "200.00",
            "commissions-0-DELETE": "",
            # Delete existing commission
            "commissions-1-id": commission2.pk,
            "commissions-1-beneficiary": contact3.pk,
            "commissions-1-value": "200.00",
            "commissions-1-DELETE": "on",
            # Add new commission
            "commissions-2-id": "",
            "commissions-2-beneficiary": contact3.pk,
            "commissions-2-value": "300.00",
            "commissions-2-DELETE": "",
        },
    )
    assert resp.status_code == status.HTTP_200_OK

    agreement.refresh_from_db()
    assert agreement.description == "Updated with inlines"

    # Verify commissions were updated
    commissions = agreement.commissions.all().order_by("value")
    assert commissions.count() == 2

    assert commissions[0].id == commission1.id
    assert commissions[0].beneficiary_id == contact1.pk
    assert commissions[0].value == Decimal("200.00")

    assert commissions[1].beneficiary_id == contact3.pk
    assert commissions[1].value == Decimal("300.00")


# ----------- Test Validation errors


def test_object_update__form_field_error(db, staff_client):
    agreement = AgreementFactory.create()

    # Send invalid data (empty required fields)
    resp = get_update_agreement_response(
        agreement,
        staff_client,
        data={
            "type": "",  # Required field
            "status": "",  # Required field
        },
        commissions_data={
            "commissions-TOTAL_FORMS": "1",
            "commissions-INITIAL_FORMS": "0",
            "commissions-MIN_NUM_FORMS": "0",
            "commissions-MAX_NUM_FORMS": "1000",
            "commissions-0-id": "",
            "commissions-0-beneficiary": "",
            "commissions-0-value": "",
            "commissions-0-DELETE": "",
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    # Check error structure
    assert resp.data == {
        "error_data": {
            "status": [{"message": "This field is required.", "code": "required"}]
        },
        "inlines_error_data": {
            "commissions": {"forms_errors": [{}], "non_forms_errors": []}
        },
    }


def test_object_update__non_form_field_error(db, staff_client):
    agreement = AgreementFactory.create()

    # Send invalid data (empty required fields)
    resp = get_update_agreement_response(
        agreement,
        staff_client,
        data={
            "type": agreement.type,  # Required field
            "status": agreement.status,  # Required field
            "valid_from": "2025-12-02",  # Required field
            "valid_until": "2025-12-01",  # Required field
        },
        commissions_data={
            "commissions-TOTAL_FORMS": "1",
            "commissions-INITIAL_FORMS": "0",
            "commissions-MIN_NUM_FORMS": "0",
            "commissions-MAX_NUM_FORMS": "1000",
            "commissions-0-id": "",
            "commissions-0-beneficiary": "",
            "commissions-0-value": "",
            "commissions-0-DELETE": "",
        },
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # Check error structure
    assert resp.data == {
        "error_data": {
            "__all__": [
                {"message": "Valid until cannot be before valid from.", "code": ""}
            ]
        },
        "inlines_error_data": {
            "commissions": {"forms_errors": [{}], "non_forms_errors": []}
        },
    }


def test_object_update__inline_missing_management_form(db, staff_client):
    agreement = AgreementFactory.create()

    # Update with invalid inline formset data
    resp = get_update_agreement_response(
        agreement,
        staff_client,
        data={
            "type": agreement.type,
            "status": agreement.status,
            "description": "Updated",
        },
        commissions_data={
            # Inline formset management form
            # Invalid commission (missing required beneficiary)
            "commissions-0-id": "",
            "commissions-0-beneficiary": "2",  # Required field
            "commissions-0-value": "100.00",
            "commissions-0-DELETE": "",
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    # Check error structure
    assert resp.data == {
        "error_data": {},
        "inlines_error_data": {
            "commissions": {
                "forms_errors": [],
                "non_forms_errors": [
                    {
                        "message": (
                            "ManagementForm data is missing or has been tampered with. "
                            "Missing fields: commissions-TOTAL_FORMS, commissions-INITIAL_FORMS. "
                            "You may need to file a bug report if the issue persists."
                        ),
                        "code": "missing_management_form",
                    }
                ],
            }
        },
    }


def test_object_update__inline_formset_form_field_error(db, staff_client):
    agreement = AgreementFactory.create(type=Agreement.TypeChoices.CONTRACT_OF_SALE)

    # Update with invalid inline formset data
    resp = get_update_agreement_response(
        agreement,
        staff_client,
        data={
            "type": agreement.type,
            "status": agreement.status,
            "description": "Updated",
        },
        commissions_data={
            # Inline formset management form
            "commissions-TOTAL_FORMS": "1",
            "commissions-INITIAL_FORMS": "0",
            "commissions-MIN_NUM_FORMS": "0",
            "commissions-MAX_NUM_FORMS": "1000",
            # Invalid commission (missing required beneficiary)
            "commissions-0-id": "",
            "commissions-0-beneficiary": "",  # Required field
            "commissions-0-value": "100.00",
            "commissions-0-DELETE": "",
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # Check error structure
    assert resp.data == {
        "error_data": {},
        "inlines_error_data": {
            "commissions": {
                "forms_errors": [{"beneficiary": ["This field is required."]}],
                "non_forms_errors": [],
            }
        },
    }


def test_object_update__inline_formset_field_and_non_form_field_error(db, staff_client):
    agreement = AgreementFactory.create(type=Agreement.TypeChoices.CONTRACT_OF_SALE)
    contact = ContactFactory.create(person=True)

    # Update with invalid inline formset data
    resp = get_update_agreement_response(
        agreement,
        staff_client,
        data={
            "type": agreement.type,
            "status": agreement.status,
            "description": "Updated",
        },
        commissions_data={
            # Inline formset management form
            "commissions-TOTAL_FORMS": "1",
            "commissions-INITIAL_FORMS": "0",
            "commissions-MIN_NUM_FORMS": "0",
            "commissions-MAX_NUM_FORMS": "1000",
            # Invalid commission (must be a company but is person)
            "commissions-0-id": "",
            "commissions-0-beneficiary": contact.id,  # Required field
            "commissions-0-value": "-100.00",
            "commissions-0-DELETE": "",
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # Check error structure
    assert resp.data == {
        "error_data": {},
        "inlines_error_data": {
            "commissions": {
                "forms_errors": [
                    {
                        "value": ["This value must be positive."],
                        "__all__": ["Beneficiary must be a company."],
                    }
                ],
                "non_forms_errors": [],
            }
        },
    }


def test_object_update__inline_formset_all_error_types(db, staff_client):
    agreement = AgreementFactory.create(type=Agreement.TypeChoices.TENANCY_AGREEMENT)
    contact1 = ContactFactory.create(company=True)
    contact2 = ContactFactory.create(person=True)

    # Update with invalid inline formset data
    resp = get_update_agreement_response(
        agreement,
        staff_client,
        data={
            "type": agreement.type,
            "status": agreement.status,
            "description": "Updated",
        },
        commissions_data={
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
            "commissions-1-beneficiary": contact2.id,  # Required field
            "commissions-1-value": "-100.00",
            "commissions-1-DELETE": "",
        },
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


def test_object_update__all_possible_error_types(db, staff_client):
    tommorow = timezone.now() + relativedelta(days=1)
    agreement = AgreementFactory.create(
        type=Agreement.TypeChoices.TENANCY_AGREEMENT,
        valid_from=tommorow,
        valid_until=timezone.now(),
    )
    contact1 = ContactFactory.create(company=True)
    contact2 = ContactFactory.create(person=True)

    # Update with invalid inline formset data
    resp = get_update_agreement_response(
        agreement,
        staff_client,
        data={
            "type": agreement.type,
            "status": agreement.status,
            "description": "Updated",
            "reservation_date": "asd",  # wrong date format -> field error
        },
        commissions_data={
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
            "commissions-1-beneficiary": contact2.id,  # Required field
            "commissions-1-value": "-100.00",
            "commissions-1-DELETE": "",
        },
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


def test_object_update__inline_permissions_required(db, no_perms_staff_client):
    agreement = AgreementFactory.create(type=Agreement.TypeChoices.CONTRACT_OF_SALE.value)
    contact = ContactFactory.create()

    # With add permission for agreement but not for commissions
    change_perm = Permission.objects.get(codename="change_agreement")

    no_perms_staff_client.user.user_permissions.set([change_perm])
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

    resp = get_update_agreement_response(
        agreement,
        no_perms_staff_client,
        data={"description": "Updated"},
        commissions_data=commissions_data,
    )

    assert resp.status_code == status.HTTP_200_OK

    # Commission should not be created without permission
    # even if data is sent
    assert AgreementCommission.objects.all().count() == 0


def test_object_update__all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement_has_change_permission_spy = mocker.spy(
        AgreementAdmin, "has_change_permission"
    )
    agreement_get_fieldsets_spy = mocker.spy(AgreementAdmin, "get_fieldsets")
    agreement_get_form_spy = mocker.spy(AgreementAdmin, "get_form")
    agreement_create_formsets_spy = mocker.spy(AgreementAdmin, "_create_formsets")
    agreement_save_form_spy = mocker.spy(AgreementAdmin, "save_form")
    agreement_save_model_spy = mocker.spy(AgreementAdmin, "save_model")
    agreement_save_related_spy = mocker.spy(AgreementAdmin, "save_related")
    agreement_construct_change_message_spy = mocker.spy(
        AgreementAdmin, "construct_change_message"
    )
    agreement_log_change_spy = mocker.spy(AgreementAdmin, "log_change")

    agreement = AgreementFactory.create()

    resp = get_update_agreement_response(
        agreement,
        staff_client,
        data={
            "type": agreement.type,
            "status": agreement.status,
            "description": "Updated",
        },
        commissions_data={
            # Inline formset management form
            "commissions-TOTAL_FORMS": "1",
            "commissions-INITIAL_FORMS": "0",
            "commissions-MIN_NUM_FORMS": "0",
            "commissions-MAX_NUM_FORMS": "1000",
        },
    )
    assert resp.status_code == status.HTTP_200_OK

    admin_site_has_permission_spy.assert_called()
    agreement_has_change_permission_spy.assert_called()
    agreement_get_fieldsets_spy.assert_called()
    agreement_get_form_spy.assert_called()
    agreement_create_formsets_spy.assert_called()
    agreement_save_form_spy.assert_called()
    agreement_save_model_spy.assert_called()
    agreement_save_related_spy.assert_called()
    agreement_construct_change_message_spy.assert_called()
    agreement_log_change_spy.assert_called()


def test_object_update__concurrent_updates(db, staff_client):
    agreement = AgreementFactory.create(description="Original")

    # First update
    resp1 = get_update_agreement_response(
        agreement,
        staff_client,
        data={
            "type": agreement.type,
            "status": agreement.status,
            "description": "First update",
        },
        commissions_data={
            # Inline formset management form
            "commissions-TOTAL_FORMS": "1",
            "commissions-INITIAL_FORMS": "0",
            "commissions-MIN_NUM_FORMS": "0",
            "commissions-MAX_NUM_FORMS": "1000",
        },
    )
    assert resp1.status_code == status.HTTP_200_OK

    # Second update
    resp2 = get_update_agreement_response(
        agreement,
        staff_client,
        data={
            "type": agreement.type,
            "status": agreement.status,
            "description": "Second update",
        },
        commissions_data={
            # Inline formset management form
            "commissions-TOTAL_FORMS": "1",
            "commissions-INITIAL_FORMS": "0",
            "commissions-MIN_NUM_FORMS": "0",
            "commissions-MAX_NUM_FORMS": "1000",
        },
    )
    assert resp2.status_code == status.HTTP_200_OK

    # Verify last update wins
    agreement.refresh_from_db()
    assert agreement.description == "Second update"


# ----------- Test not permitted


def test_object_update__view_permission_not_sufficient(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    # With only view permission
    view_perm = Permission.objects.get(codename="view_agreement")
    no_perms_staff_client.user.user_permissions.set([view_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.put(
        f"/api/real_estate/agreement/{agreement.pk}/",
        data={"description": "Updated"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify object was NOT updated
    agreement.refresh_from_db()
    assert agreement.description != "Updated"


def test_object_update__delete_permission_not_sufficient(db, no_perms_staff_client):
    agreement = AgreementFactory.create(description="Original")

    # With only delete permission
    delete_perm = Permission.objects.get(codename="delete_agreement")

    no_perms_staff_client.user.user_permissions.set([delete_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.put(
        f"/api/real_estate/agreement/{agreement.pk}/",
        data={"description": "Updated"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify object was NOT updated
    agreement.refresh_from_db()
    assert agreement.description == "Original"


def test_object_update__add_permission_not_sufficient(db, no_perms_staff_client):
    agreement = AgreementFactory.create(description="Original")

    # With only add permission
    add_perm = Permission.objects.get(codename="add_agreement")

    no_perms_staff_client.user.user_permissions.set([add_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.put(
        f"/api/real_estate/agreement/{agreement.pk}/",
        data={"description": "Updated"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify object was NOT updated
    agreement.refresh_from_db()
    assert agreement.description == "Original"
