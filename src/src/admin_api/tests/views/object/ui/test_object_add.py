from ast import Add
import pytest
from django.contrib import admin
from django.contrib.auth.models import Permission, Group
from rest_framework import status

from admin_api.model_admins import AgreementAdmin
from backend.organization.models import User
from ..utils import get_object_add_data


AGREEMENT_OBJECT_ADD_PATH = "/api/real_estate/agreement/add/"


# ----------- Test Permissions and errors


def test_object_add__only_get_allowed(staff_client, db):
    for method in ["post", "put", "patch", "delete"]:
        resp = getattr(staff_client, method)(AGREEMENT_OBJECT_ADD_PATH)
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_object_add__base_permission_check(non_staff_client, db, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    resp = non_staff_client.get(AGREEMENT_OBJECT_ADD_PATH)
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_object_add__base_admin_apiview_errors(staff_client, db):
    # Non-existent app
    resp = staff_client.get("/api/notanapp/agreement/add/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Non-existent model (real_estate app exists)
    resp = staff_client.get("/api/real_estate/notamodel/add/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Model exists but no admin registered
    resp = staff_client.get("/api/common/country/add/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}


def test_object_add__add_permission_required(db, no_perms_staff_client):
    # No permission
    resp = no_perms_staff_client.get(AGREEMENT_OBJECT_ADD_PATH)
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With add permission
    add_perm = Permission.objects.get(codename="add_agreement")
    no_perms_staff_client.user.user_permissions.set([add_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(AGREEMENT_OBJECT_ADD_PATH)
    assert resp.status_code == status.HTTP_200_OK


# ----------- Test functionality


def test_object_add__structure(db, staff_client):
    resp = staff_client.get(AGREEMENT_OBJECT_ADD_PATH)
    assert resp.status_code == status.HTTP_200_OK

    expected_data = get_object_add_data(staff_client.user)
    assert resp.data["app"] == expected_data["app"]
    assert resp.data["model"] == expected_data["model"]
    assert resp.data["fieldsets"] == expected_data["fieldsets"]
    assert resp.data["readonly_fields"] == expected_data["readonly_fields"]
    assert resp.data["fields"] == expected_data["fields"]
    assert resp.data["inlines"] == expected_data["inlines"]
    assert resp.data == expected_data


def test_object_add__related_field_permissions(db, no_perms_staff_client):
    add_perm = Permission.objects.get(codename="add_agreement")
    agreement_commission_add_perm = Permission.objects.get(
        codename="add_agreementcommission"
    )
    project_view_perm = Permission.objects.get(codename="view_project")
    project_add_perm = Permission.objects.get(codename="add_project")
    project_change_perm = Permission.objects.get(codename="change_project")
    project_delete_perm = Permission.objects.get(codename="delete_project")

    # Only add permission for agreement
    no_perms_staff_client.user.user_permissions.set([add_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(AGREEMENT_OBJECT_ADD_PATH)
    assert resp.status_code == status.HTTP_200_OK

    # since to permissions on AgreementCommission
    # inline will not be included
    assert resp.data["inlines"] == []

    assert resp.data["fields"]["project"]["permissions"]["view"] is False
    assert resp.data["fields"]["project"]["permissions"]["add"] is False
    assert resp.data["fields"]["project"]["permissions"]["change"] is False
    assert resp.data["fields"]["project"]["permissions"]["delete"] is False

    # With project and AgreementCommission permissions
    no_perms_staff_client.user.user_permissions.set(
        [
            add_perm,
            agreement_commission_add_perm,
            project_view_perm,
            project_add_perm,
            project_change_perm,
            project_delete_perm,
        ]
    )
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(AGREEMENT_OBJECT_ADD_PATH)
    assert resp.status_code == status.HTTP_200_OK

    assert resp.data["fields"]["project"]["permissions"]["view"] is True
    assert resp.data["fields"]["project"]["permissions"]["add"] is True
    assert resp.data["fields"]["project"]["permissions"]["change"] is True
    assert resp.data["fields"]["project"]["permissions"]["delete"] is True

    expected_data = get_object_add_data(no_perms_staff_client.user)

    # inline will be included
    assert len(resp.data["inlines"]) == 1

    assert resp.data["app"] == expected_data["app"]
    assert resp.data["model"] == expected_data["model"]
    assert resp.data["fieldsets"] == expected_data["fieldsets"]
    assert resp.data["readonly_fields"] == expected_data["readonly_fields"]

    for field_name in resp.data["fields"]:
        assert resp.data["fields"][field_name] == expected_data["fields"][field_name]

    assert resp.data["inlines"] == expected_data["inlines"]

    assert resp.data == expected_data


def test_object_add__all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement_has_add_permission_spy = mocker.spy(AgreementAdmin, "has_add_permission")
    agreement_get_fieldsets_spy = mocker.spy(AgreementAdmin, "get_fieldsets")
    agreement_get_form_spy = mocker.spy(AgreementAdmin, "get_form")
    agreement_get_readonly_fields_spy = mocker.spy(AgreementAdmin, "get_readonly_fields")
    agreement_get_exclude_spy = mocker.spy(AgreementAdmin, "get_exclude")
    agreement_get_changeform_initial_data_spy = mocker.spy(
        AgreementAdmin, "get_changeform_initial_data"
    )
    agreement_create_formsets_spy = mocker.spy(AgreementAdmin, "_create_formsets")

    resp = staff_client.get(AGREEMENT_OBJECT_ADD_PATH)
    assert resp.status_code == status.HTTP_200_OK

    admin_site_has_permission_spy.assert_called()
    agreement_has_add_permission_spy.assert_called()
    agreement_get_fieldsets_spy.assert_called()
    agreement_get_form_spy.assert_called()
    agreement_get_readonly_fields_spy.assert_called()
    agreement_get_exclude_spy.assert_called()
    agreement_get_changeform_initial_data_spy.assert_called()
    agreement_create_formsets_spy.assert_called()


def test_object_add__concurrent_requests_same_results(db, staff_client):
    resp1 = staff_client.get(AGREEMENT_OBJECT_ADD_PATH)
    resp2 = staff_client.get(AGREEMENT_OBJECT_ADD_PATH)

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
        ["view", "change", "add", "delete"],
    ],
)
def test_object_add__inline_permissions(db, no_perms_staff_client, permissions):
    add_perm = Permission.objects.get(codename="add_agreement")
    all_inline_perms = Permission.objects.filter(
        codename__in=[p + "_agreementcommission" for p in permissions]
    )
    all_perms = [add_perm] + [p for p in all_inline_perms]

    no_perms_staff_client.user.user_permissions.set(all_perms)
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )
    resp = no_perms_staff_client.get(AGREEMENT_OBJECT_ADD_PATH)
    assert resp.status_code == status.HTTP_200_OK

    expected_data = get_object_add_data(no_perms_staff_client.user)
    assert resp.data["app"] == expected_data["app"]
    assert resp.data["model"] == expected_data["model"]
    assert resp.data["fieldsets"] == expected_data["fieldsets"]
    assert resp.data["readonly_fields"] == expected_data["readonly_fields"]
    assert resp.data["fields"] == expected_data["fields"]
    assert resp.data["inlines"] == expected_data["inlines"]
    assert resp.data == expected_data


# This test is for the special occasion
# where the object has a many to many field
# and set through filter_(horizontal/vertical)
def test_object_add__group_with_many_to_many_field(
    db, no_perms_staff_client, settings_no_tz
):
    add_group_perm = Permission.objects.get(codename="add_group")
    view_permission_perm = Permission.objects.get(codename="view_permission")
    all_perms = [add_group_perm, view_permission_perm]

    no_perms_staff_client.user.user_permissions.set(all_perms)
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get("/api/auth/group/add/")
    assert resp.status_code == status.HTTP_200_OK

    assert resp.data == {
        "object_repr": None,
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
                "initial": None,
            },
            "permissions": {
                "type": "ModelMultipleChoiceField",
                "label": "Permissions",
                "required": False,
                "help_text": "Hold down “Control”, or “Command” on a Mac, to select more than one.",
                "initial": [],
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
