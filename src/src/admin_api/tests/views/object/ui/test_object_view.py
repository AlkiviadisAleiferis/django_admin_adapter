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
from ..utils import get_object_view_data


# ----------- Test Permissions and errors


def test_object_view__only_get_allowed(staff_client, db):
    agreement = AgreementFactory.create()
    for method in ["post", "put", "patch", "delete"]:
        resp = getattr(staff_client, method)(
            f"/api/real_estate/agreement/{agreement.pk}/view/"
        )
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_object_view__base_permission_check(non_staff_client, db, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement = AgreementFactory.create()
    resp = non_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_object_view__base_admin_apiview_errors(staff_client, db):
    # Non-existent app
    resp = staff_client.get("/api/notanapp/agreement/1/view/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Non-existent model (real_estate app exists)
    resp = staff_client.get("/api/real_estate/notamodel/1/view/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Model exists but no admin registered
    resp = staff_client.get("/api/common/country/1/view/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}


def test_object_view__view_permission_required(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    # No permission
    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With view permission
    view_perm = Permission.objects.get(codename="view_agreement")
    no_perms_staff_client.user.user_permissions.set([view_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )
    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_200_OK

    # With change permission
    change_perm = Permission.objects.get(codename="change_agreement")
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    # With delete permission
    delete_perm = Permission.objects.get(codename="delete_agreement")
    no_perms_staff_client.user.user_permissions.set([delete_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With add permission
    add_perm = Permission.objects.get(codename="add_agreement")
    no_perms_staff_client.user.user_permissions.set([add_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_object_view__object_not_found(staff_client):
    resp = staff_client.get("/api/real_estate/agreement/999999999999/view/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ----------- Test functionality


def test_object_view__structure(db, staff_client, settings_no_tz):
    agreement = AgreementFactory.create()
    contact = ContactFactory.create()
    AgreementCommission.objects.create(
        agreement=agreement, beneficiary=contact, value=222.00
    )

    resp = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_200_OK

    expected_data = get_object_view_data(agreement, staff_client.user)
    assert resp.data["object_repr"] == expected_data["object_repr"]
    assert resp.data["fieldsets"] == expected_data["fieldsets"]
    assert resp.data["permissions"] == expected_data["permissions"]
    assert resp.data["inlines"] == expected_data["inlines"]
    for field in resp.data["object"]:
        assert resp.data["object"][field] == expected_data["object"][field]
    assert resp.data["object"] == expected_data["object"]
    assert resp.data == expected_data


def test_object_view__permissions_reflect_permissions_in_data(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    view_perm = Permission.objects.get(codename="view_agreement")
    change_perm = Permission.objects.get(codename="change_agreement")
    delete_perm = Permission.objects.get(codename="delete_agreement")

    project_view_perm = Permission.objects.get(codename="view_project")
    project_change_perm = Permission.objects.get(codename="change_project")
    project_delete_perm = Permission.objects.get(codename="delete_project")

    # Only view permission
    no_perms_staff_client.user.user_permissions.set([view_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["permissions"]["view"] is True
    assert resp.data["permissions"]["change"] is False
    assert resp.data["permissions"]["delete"] is False

    # View and change permissions
    no_perms_staff_client.user.user_permissions.set([view_perm, change_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["permissions"]["view"] is True
    assert resp.data["permissions"]["change"] is True
    assert resp.data["permissions"]["delete"] is False

    # All permissions
    no_perms_staff_client.user.user_permissions.set([view_perm, change_perm, delete_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["permissions"]["view"] is True
    assert resp.data["permissions"]["change"] is True
    assert resp.data["permissions"]["delete"] is True

    no_perms_staff_client.user.user_permissions.set(
        [view_perm, project_view_perm, project_change_perm, project_delete_perm]
    )
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["object"]["project"]["permissions"]["view"] is True
    assert resp.data["object"]["project"]["permissions"]["change"] is True
    assert resp.data["object"]["project"]["permissions"]["delete"] is True


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
def test_object_view__inline_permissions(
    db, no_perms_staff_client, permissions, settings_no_tz
):
    agreement = AgreementFactory.create()
    contact = ContactFactory.create()
    AgreementCommission.objects.create(
        agreement=agreement, beneficiary=contact, value=222.00
    )

    view_perm = Permission.objects.get(codename="view_agreement")
    all_inline_perms = Permission.objects.filter(
        codename__in=[p + "_agreementcommission" for p in permissions]
    )
    all_perms = [view_perm] + [p for p in all_inline_perms]

    no_perms_staff_client.user.user_permissions.set(all_perms)
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_200_OK

    expected_data = get_object_view_data(agreement, no_perms_staff_client.user)
    assert resp.data["object_repr"] == expected_data["object_repr"]
    assert resp.data["fieldsets"] == expected_data["fieldsets"]
    assert resp.data["permissions"] == expected_data["permissions"]
    assert resp.data["inlines"] == expected_data["inlines"]
    for field in resp.data["object"]:
        assert resp.data["object"][field] == expected_data["object"][field]
    assert resp.data["object"] == expected_data["object"]
    assert resp.data == expected_data


def test_object_view__multiple_objects(db, staff_client, settings_no_tz):
    agreement1 = AgreementFactory.create()
    contact = ContactFactory.create()
    AgreementCommission.objects.create(
        agreement=agreement1, beneficiary=contact, value=222.00
    )
    agreement2 = AgreementFactory.create()

    resp1 = staff_client.get(f"/api/real_estate/agreement/{agreement1.pk}/view/")
    resp2 = staff_client.get(f"/api/real_estate/agreement/{agreement2.pk}/view/")

    assert resp1.status_code == status.HTTP_200_OK
    expected_data = get_object_view_data(agreement1, staff_client.user)
    assert resp1.data["object_repr"] == expected_data["object_repr"]
    assert resp1.data["fieldsets"] == expected_data["fieldsets"]
    assert resp1.data["permissions"] == expected_data["permissions"]
    assert resp1.data["inlines"] == expected_data["inlines"]
    assert resp1.data["object"] == expected_data["object"]
    assert resp1.data == expected_data

    assert resp2.status_code == status.HTTP_200_OK
    expected_data = get_object_view_data(agreement2, staff_client.user)
    assert resp2.data["object_repr"] == expected_data["object_repr"]
    assert resp2.data["fieldsets"] == expected_data["fieldsets"]
    assert resp2.data["permissions"] == expected_data["permissions"]
    assert resp2.data["inlines"] == expected_data["inlines"]
    assert resp2.data["object"] == expected_data["object"]
    assert resp2.data == expected_data


def test_object_view__all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement_has_view_permission_spy = mocker.spy(AgreementAdmin, "has_view_permission")
    agreement_has_change_permission_spy = mocker.spy(
        AgreementAdmin, "has_change_permission"
    )
    agreement_has_delete_permission_spy = mocker.spy(
        AgreementAdmin, "has_delete_permission"
    )
    agreement_get_fieldsets_spy = mocker.spy(AgreementAdmin, "get_fieldsets")
    agreement_get_inline_instances_spy = mocker.spy(
        AgreementAdmin, "get_inline_instances"
    )

    agreement = AgreementFactory.create()
    resp = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    assert resp.status_code == status.HTTP_200_OK

    admin_site_has_permission_spy.assert_called()
    agreement_has_view_permission_spy.assert_called()
    agreement_has_change_permission_spy.assert_called()
    agreement_has_delete_permission_spy.assert_called()
    agreement_get_fieldsets_spy.assert_called()
    agreement_get_inline_instances_spy.assert_called()


def test_object_view__concurrent_requests_same_results(db, staff_client):
    agreement = AgreementFactory.create()

    resp1 = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")
    resp2 = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/view/")

    assert resp1.status_code == status.HTTP_200_OK
    assert resp2.status_code == status.HTTP_200_OK
    assert resp1.data == resp2.data


# This test is for the special occasion
# where the object has a many to many field
# and set through filter_(horizontal/vertical)
def test_object_view__group_with_many_to_many_field(
    db, no_perms_staff_client, settings_no_tz
):
    view_group_perm = Permission.objects.get(codename="view_group")
    view_permission_perm = Permission.objects.get(codename="view_permission")
    change_permission_perm = Permission.objects.get(codename="change_permission")
    all_perms = [view_group_perm, view_permission_perm, change_permission_perm]

    group = Group.objects.create(name="Newgroup")
    group.permissions.set([view_permission_perm, change_permission_perm])

    no_perms_staff_client.user.user_permissions.set(all_perms)
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/auth/group/{group.pk}/view/")
    assert resp.status_code == status.HTTP_200_OK

    assert resp.data == {
        "object_repr": "Newgroup",
        "fieldsets": [(None, {"fields": ["name", "permissions"]})],
        "object": {
            "name": {"type": "CharField", "value": "Newgroup", "help_text": ""},
            "permissions": {
                "type": "ManyRelatedField",
                "model": "group",
                "app": "auth",
                "value": [
                    {
                        "type": "RelatedField",
                        "pk": change_permission_perm.pk,
                        "model": "permission",
                        "app": "auth",
                        "value": str(change_permission_perm),
                        "help_text": "",
                        "permissions": {
                            "view": False,  # NO model admin module permission
                            "add": False,
                            "change": False,
                            "delete": False,
                        },
                    },
                    {
                        "type": "RelatedField",
                        "pk": view_permission_perm.pk,
                        "model": "permission",
                        "app": "auth",
                        "value": str(view_permission_perm),
                        "help_text": "",
                        "permissions": {
                            "view": False,  # NO model admin module permission
                            "add": False,
                            "change": False,
                            "delete": False,
                        },
                    },
                ],
                "help_text": "",
            },
            "pk": {"type": "IntegerField", "value": group.pk, "help_text": ""},
        },
        "permissions": {
            "view": True,
            "add": False,
            "change": False,
            "delete": False,
            "history": True,
        },
        "inlines": [],
        "extra_data": None,
    }
