import pytest
from django.contrib import admin
from django.contrib.auth.models import Permission, Group
from rest_framework import status

from admin_api.model_admins import AgreementAdmin
from backend.tests.factories import (
    AgreementFactory,
    ContactFactory,
    UserFactory,
    ProjectFactory,
    PropertyFactory,
)
from backend.real_estate.models import AgreementCommission
from backend.organization.models import User
from ..utils import get_object_edit_data


# ----------- Test Permissions and errors


def test_object_edit__only_get_allowed(staff_client, db):
    agreement = AgreementFactory.create()
    for method in ["post", "put", "patch", "delete"]:
        resp = getattr(staff_client, method)(
            f"/api/real_estate/agreement/{agreement.pk}/edit/"
        )
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_object_edit__base_permission_check(non_staff_client, db, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement = AgreementFactory.create()
    resp = non_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_object_edit__base_admin_apiview_errors(staff_client, db):
    # Non-existent app
    resp = staff_client.get("/api/notanapp/agreement/1/edit/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Non-existent model (real_estate app exists)
    resp = staff_client.get("/api/real_estate/notamodel/1/edit/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Model exists but no admin registered
    resp = staff_client.get("/api/common/country/1/edit/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}


def test_object_edit__change_permission_required(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    # No permission
    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With change permission
    change_perm = Permission.objects.get(codename="change_agreement")
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")
    assert resp.status_code == status.HTTP_200_OK


def test_object_edit__object_not_found(staff_client):
    resp = staff_client.get("/api/real_estate/agreement/999999999999/edit/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ----------- Test functionality


def test_object_edit__structure(db, staff_client, settings_no_tz):
    agreement = AgreementFactory.create()
    contact = ContactFactory.create()

    AgreementCommission.objects.create(
        agreement=agreement,
        beneficiary=contact,
        value=222.00,
    )

    resp = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")
    assert resp.status_code == status.HTTP_200_OK

    expected_data = get_object_edit_data(staff_client.user, agreement)

    assert resp.data["object_repr"] == expected_data["object_repr"]
    assert resp.data["app"] == expected_data["app"]
    assert resp.data["model"] == expected_data["model"]
    assert resp.data["fieldsets"] == expected_data["fieldsets"]
    assert resp.data["readonly_fields"] == expected_data["readonly_fields"]
    assert resp.data["fields"] == expected_data["fields"]
    assert resp.data["inlines"] == expected_data["inlines"]
    assert resp.data == expected_data


def test_object_edit__structure_without_inlines(db, staff_client, settings_no_tz):
    agreement = AgreementFactory.create()

    resp = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")
    assert resp.status_code == status.HTTP_200_OK

    expected_data = get_object_edit_data(staff_client.user, agreement)

    assert resp.data["object_repr"] == expected_data["object_repr"]
    assert resp.data["app"] == expected_data["app"]
    assert resp.data["model"] == expected_data["model"]
    assert resp.data["fieldsets"] == expected_data["fieldsets"]
    assert resp.data["readonly_fields"] == expected_data["readonly_fields"]
    assert resp.data["fields"] == expected_data["fields"]
    assert resp.data["inlines"] == expected_data["inlines"]
    assert resp.data == expected_data


def test_object_edit__related_field_permissions(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    change_perm = Permission.objects.get(codename="change_agreement")
    agreement_commission_change_perm = Permission.objects.get(
        codename="change_agreementcommission"
    )
    project_view_perm = Permission.objects.get(codename="view_project")
    project_add_perm = Permission.objects.get(codename="add_project")
    project_change_perm = Permission.objects.get(codename="change_project")
    project_delete_perm = Permission.objects.get(codename="delete_project")

    # Only change permission for agreement
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")
    assert resp.status_code == status.HTTP_200_OK

    # since no permissions on AgreementCommission, inline will not be included
    assert resp.data["inlines"] == []

    assert resp.data["fields"]["project"]["permissions"]["view"] is False
    assert resp.data["fields"]["project"]["permissions"]["add"] is False
    assert resp.data["fields"]["project"]["permissions"]["change"] is False
    assert resp.data["fields"]["project"]["permissions"]["delete"] is False

    # With project and AgreementCommission permissions
    no_perms_staff_client.user.user_permissions.set(
        [
            change_perm,
            agreement_commission_change_perm,
            project_view_perm,
            project_add_perm,
            project_change_perm,
            project_delete_perm,
        ]
    )
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")
    assert resp.status_code == status.HTTP_200_OK

    assert resp.data["fields"]["project"]["permissions"]["view"] is True
    assert resp.data["fields"]["project"]["permissions"]["add"] is True
    assert resp.data["fields"]["project"]["permissions"]["change"] is True
    assert resp.data["fields"]["project"]["permissions"]["delete"] is True

    # inline will be included
    assert len(resp.data["inlines"]) == 1


def test_object_edit__all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement_has_change_permission_spy = mocker.spy(
        AgreementAdmin, "has_change_permission"
    )
    agreement_get_fieldsets_spy = mocker.spy(AgreementAdmin, "get_fieldsets")
    agreement_get_form_spy = mocker.spy(AgreementAdmin, "get_form")
    agreement_get_readonly_fields_spy = mocker.spy(AgreementAdmin, "get_readonly_fields")
    agreement_get_exclude_spy = mocker.spy(AgreementAdmin, "get_exclude")
    agreement_create_formsets_spy = mocker.spy(AgreementAdmin, "_create_formsets")

    agreement = AgreementFactory.create()
    resp = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")
    assert resp.status_code == status.HTTP_200_OK

    admin_site_has_permission_spy.assert_called()
    agreement_has_change_permission_spy.assert_called()
    agreement_get_fieldsets_spy.assert_called()
    agreement_get_form_spy.assert_called()
    agreement_get_readonly_fields_spy.assert_called()
    agreement_get_exclude_spy.assert_called()
    agreement_create_formsets_spy.assert_called()


def test_object_edit__concurrent_requests_same_results(db, staff_client):
    agreement = AgreementFactory.create()

    resp1 = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")
    resp2 = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")

    assert resp1.status_code == status.HTTP_200_OK
    assert resp2.status_code == status.HTTP_200_OK
    assert resp1.data == resp2.data


# combinations firmula : n!/(r!*(n-r)!)
# n --> number of permissions
# r --> number of permissions to choose
@pytest.mark.parametrize(
    "permissions",
    [
        ["view"],
        ["change"],
        ["add"],
        ["delete"],
        #
        ["view", "change"],
        ["view", "add"],
        ["view", "delete"],
        ["change", "add"],
        ["change", "delete"],
        ["add", "delete"],
        #
        ["view", "change", "add"],
        ["view", "add", "delete"],
        ["view", "change", "delete"],
        ["change", "add", "delete"],
        #
        #
        ["view", "change", "add", "delete"],
    ],
)
def test_object_edit__inline_permissions(
    db, no_perms_staff_client, permissions, settings_no_tz
):
    agreement = AgreementFactory.create()
    contact = ContactFactory.create()
    AgreementCommission.objects.create(
        agreement=agreement, beneficiary=contact, value=222.00
    )

    change_perm = Permission.objects.get(codename="change_agreement")
    all_inline_perms = Permission.objects.filter(
        codename__in=[p + "_agreementcommission" for p in permissions]
    )
    all_perms = [change_perm] + [p for p in all_inline_perms]

    no_perms_staff_client.user.user_permissions.set(all_perms)
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")
    assert resp.status_code == status.HTTP_200_OK

    expected_data = get_object_edit_data(no_perms_staff_client.user, agreement)
    assert resp.data["object_repr"] == expected_data["object_repr"]
    assert resp.data["app"] == expected_data["app"]
    assert resp.data["model"] == expected_data["model"]
    assert resp.data["fieldsets"] == expected_data["fieldsets"]
    assert resp.data["readonly_fields"] == expected_data["readonly_fields"]
    assert resp.data["fields"] == expected_data["fields"]
    assert resp.data["inlines"] == expected_data["inlines"]
    assert resp.data == expected_data


def test_object_edit__management_form_reflects_existing_forms(db, staff_client):
    agreement = AgreementFactory.create()
    contact1 = ContactFactory.create()
    contact2 = ContactFactory.create()
    AgreementCommission.objects.create(
        agreement=agreement, beneficiary=contact1, value=100.00
    )
    AgreementCommission.objects.create(
        agreement=agreement, beneficiary=contact2, value=200.00
    )

    resp = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/edit/")
    assert resp.status_code == status.HTTP_200_OK

    commission_inline = resp.data["inlines"][0]
    management_form = commission_inline["management_form"]

    # INITIAL_FORMS should be 2 (existing commissions)
    assert management_form["fields"]["INITIAL_FORMS"]["initial"] == 2

    # TOTAL_FORMS should be 3 (2 existing + 1 extra)
    assert management_form["fields"]["TOTAL_FORMS"]["initial"] == 3


def test_object_edit__multiple_different_objects(db, staff_client, settings_no_tz):
    agreement1 = AgreementFactory.create(description="Agreement 1")
    agreement2 = AgreementFactory.create(description="Agreement 2")

    resp1 = staff_client.get(f"/api/real_estate/agreement/{agreement1.pk}/edit/")
    resp2 = staff_client.get(f"/api/real_estate/agreement/{agreement2.pk}/edit/")

    assert resp1.status_code == status.HTTP_200_OK
    assert resp2.status_code == status.HTTP_200_OK

    # Should have different object_repr
    assert resp1.data["object_repr"] == str(agreement1)
    assert resp2.data["object_repr"] == str(agreement2)
    assert resp1.data["object_repr"] != resp2.data["object_repr"]

    # Should have different initial values
    assert resp1.data["fields"]["description"]["initial"] == "Agreement 1"
    assert resp2.data["fields"]["description"]["initial"] == "Agreement 2"


# This test is for the special occasion
# where the object has a many to many field
# and set through filter_(horizontal/vertical)
def test_object_edit__group_with_many_to_many_field(
    db, no_perms_staff_client, settings_no_tz
):
    change_group_perm = Permission.objects.get(codename="change_group")
    view_permission_perm = Permission.objects.get(codename="view_permission")
    change_permission_perm = Permission.objects.get(codename="change_permission")
    all_perms = [change_group_perm, view_permission_perm, change_permission_perm]

    group = Group.objects.create(name="Newgroup")
    group.permissions.set([view_permission_perm, change_permission_perm])

    no_perms_staff_client.user.user_permissions.set(all_perms)
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/auth/group/{group.pk}/edit/")
    assert resp.status_code == status.HTTP_200_OK

    assert resp.data == {
        "object_repr": "Newgroup",
        "model": "group",
        "app": "auth",
        "fieldsets": [(None, {"fields": ["name", "permissions"]})],
        "readonly_fields": {},
        "fields": {
            "name": {
                "type": "CharField",
                "label": "Name",
                "required": True,
                "help_text": "",
                "initial": "Newgroup",
            },
            "permissions": {
                "type": "ModelMultipleChoiceField",
                "label": "Permissions",
                "required": False,
                "help_text": "Hold down “Control”, or “Command” on a Mac, to select more than one.",
                "initial": [change_permission_perm.pk, view_permission_perm.pk],
                "choices": [
                    {
                        "value": p.pk,
                        "label": str(p),
                    }
                    for p in Permission.objects.all()
                ],
            },
        },
        "prefix": None,
        "inlines": [],
        "extra_data": None,
    }
