from copy import deepcopy
import pytest

from django.contrib import admin
from rest_framework.test import force_authenticate
from rest_framework import status

from .utils import get_sidebar_registry
from admin_api.model_admins import (
    ProjectAdmin,
    PropertyAdmin,
    ContactAdmin,
    EmailAdmin,
    PermissionAdmin,
    AgreementAdmin,
)
from admin_api.user import UserAdmin
from django.contrib.auth.admin import GroupAdmin
from admin_api.tests.utils import get_view
from backend.organization.models import User
from django_admin_adapter.viewmap import VIEWMAP


def test_base_info_only_get_allowed(superuser_client):
    for method in ["post", "put", "patch", "delete"]:
        resp = getattr(superuser_client, method)("/api/" + VIEWMAP["base_info"][0])
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_base_info_base_permission_check(non_staff_client):
    resp = non_staff_client.get("/api/" + VIEWMAP["base_info"][0])
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_base_info_returns_expected_structure(
    no_perms_staff_client, staff_client, superuser_client
):
    response = no_perms_staff_client.get("/api/" + VIEWMAP["base_info"][0])
    assert response.status_code == status.HTTP_200_OK
    expected_data = get_sidebar_registry(no_perms_staff_client.user)

    for idx, entry in enumerate(response.data["sidebar"]):
        if entry["type"] == "dropdown":
            for idx2, entry2 in enumerate(
                response.data["sidebar"][idx]["dropdown_entries"]
            ):
                assert entry2 == expected_data["sidebar"][idx]["dropdown_entries"][idx2]
        else:
            assert entry == expected_data["sidebar"][idx]

    assert response.data["sidebar"] == expected_data["sidebar"]
    assert response.data["profile"] == expected_data["profile"]
    assert response.data["extra"] == expected_data["extra"]
    assert response.data == expected_data

    # ----------------------------
    # with permissions
    response = staff_client.get("/api/" + VIEWMAP["base_info"][0])
    assert response.status_code == status.HTTP_200_OK
    expected_data = get_sidebar_registry(staff_client.user)

    for idx, entry in enumerate(response.data["sidebar"]):
        if entry["type"] == "dropdown":
            for idx2, entry2 in enumerate(
                response.data["sidebar"][idx]["dropdown_entries"]
            ):
                assert entry2 == expected_data["sidebar"][idx]["dropdown_entries"][idx2]
        else:
            assert entry == expected_data["sidebar"][idx]

    assert response.data["sidebar"] == expected_data["sidebar"]
    assert response.data["profile"] == expected_data["profile"]
    assert response.data["extra"] == expected_data["extra"]
    assert response.data == expected_data

    # ----------------------------
    # with superuser
    #
    # this also tests cases
    # where the ModelAdmin has revoked permissions
    # through their corresponding method
    response = superuser_client.get("/api/" + VIEWMAP["base_info"][0])
    assert response.status_code == status.HTTP_200_OK
    expected_data = get_sidebar_registry(superuser_client.user)

    for idx, entry in enumerate(response.data["sidebar"]):
        if entry["type"] == "dropdown":
            for idx2, entry2 in enumerate(
                response.data["sidebar"][idx]["dropdown_entries"]
            ):
                assert entry2 == expected_data["sidebar"][idx]["dropdown_entries"][idx2]
        else:
            assert entry == expected_data["sidebar"][idx]

    assert response.data["sidebar"] == expected_data["sidebar"]
    assert response.data["profile"] == expected_data["profile"]
    assert response.data["extra"] == expected_data["extra"]
    assert response.data == expected_data


def test_base_info_all_the_proper_methods_called(staff_client, mocker):
    admin_site_spy = mocker.spy(admin.site, "has_permission")

    permission_module_perm_spy = mocker.spy(PermissionAdmin, "has_module_permission")
    # permission `has_view_or_change_permission` not called
    # because it fails at `has_module_permission`
    # and no  `has_view/change/delete_permission` are called
    permission_view_or_change_perm_spy = mocker.spy(
        PermissionAdmin, "has_view_or_change_permission"
    )
    permission_view_perm_spy = mocker.spy(PermissionAdmin, "has_view_permission")
    permission_add_perm_spy = mocker.spy(PermissionAdmin, "has_add_permission")
    permission_change_perm_spy = mocker.spy(PermissionAdmin, "has_change_permission")
    permission_delete_perm_spy = mocker.spy(PermissionAdmin, "has_delete_permission")

    group_module_perm_spy = mocker.spy(GroupAdmin, "has_module_permission")
    group_view_perm_spy = mocker.spy(GroupAdmin, "has_view_or_change_permission")
    group_add_perm_spy = mocker.spy(GroupAdmin, "has_add_permission")
    group_delete_perm_spy = mocker.spy(GroupAdmin, "has_delete_permission")

    user_module_perm_spy = mocker.spy(UserAdmin, "has_module_permission")
    user_view_perm_spy = mocker.spy(UserAdmin, "has_view_or_change_permission")
    user_change_perm_spy = mocker.spy(UserAdmin, "has_change_permission")
    user_add_perm_spy = mocker.spy(UserAdmin, "has_add_permission")
    user_delete_perm_spy = mocker.spy(UserAdmin, "has_delete_permission")

    project_module_perm_spy = mocker.spy(ProjectAdmin, "has_module_permission")
    project_view_perm_spy = mocker.spy(ProjectAdmin, "has_view_or_change_permission")
    project_add_perm_spy = mocker.spy(ProjectAdmin, "has_add_permission")
    project_delete_perm_spy = mocker.spy(ProjectAdmin, "has_delete_permission")

    property_module_perm_spy = mocker.spy(PropertyAdmin, "has_module_permission")
    property_view_perm_spy = mocker.spy(PropertyAdmin, "has_view_or_change_permission")
    property_add_perm_spy = mocker.spy(PropertyAdmin, "has_add_permission")
    property_delete_perm_spy = mocker.spy(PropertyAdmin, "has_delete_permission")

    agreement_module_perm_spy = mocker.spy(AgreementAdmin, "has_module_permission")
    agreement_view_perm_spy = mocker.spy(AgreementAdmin, "has_view_or_change_permission")
    agreement_add_perm_spy = mocker.spy(AgreementAdmin, "has_add_permission")
    agreement_delete_perm_spy = mocker.spy(AgreementAdmin, "has_delete_permission")

    contact_module_perm_spy = mocker.spy(ContactAdmin, "has_module_permission")
    contact_view_perm_spy = mocker.spy(ContactAdmin, "has_view_or_change_permission")
    contact_add_perm_spy = mocker.spy(ContactAdmin, "has_add_permission")
    contact_delete_perm_spy = mocker.spy(ContactAdmin, "has_delete_permission")

    email_module_perm_spy = mocker.spy(EmailAdmin, "has_module_permission")
    email_view_perm_spy = mocker.spy(EmailAdmin, "has_view_or_change_permission")
    email_add_perm_spy = mocker.spy(EmailAdmin, "has_add_permission")
    email_delete_perm_spy = mocker.spy(EmailAdmin, "has_delete_permission")

    response = staff_client.get("/api/" + VIEWMAP["base_info"][0])

    assert response.status_code == status.HTTP_200_OK
    assert response.data == get_sidebar_registry(staff_client.user)

    admin_site_spy.assert_called()

    permission_module_perm_spy.assert_called()

    permission_view_perm_spy.assert_not_called()
    permission_view_or_change_perm_spy.assert_not_called()
    permission_change_perm_spy.assert_not_called()
    permission_add_perm_spy.assert_not_called()
    permission_delete_perm_spy.assert_not_called()

    group_module_perm_spy.assert_called()
    group_view_perm_spy.assert_called()
    group_add_perm_spy.assert_called()
    group_delete_perm_spy.assert_called()

    user_module_perm_spy.assert_called()
    user_view_perm_spy.assert_called()
    user_change_perm_spy.assert_called()
    user_add_perm_spy.assert_called()
    user_delete_perm_spy.assert_called()

    project_module_perm_spy.assert_called()
    project_view_perm_spy.assert_called()
    project_add_perm_spy.assert_called()
    project_delete_perm_spy.assert_called()

    property_module_perm_spy.assert_called()
    property_view_perm_spy.assert_called()
    property_add_perm_spy.assert_called()
    property_delete_perm_spy.assert_called()

    agreement_module_perm_spy.assert_called()
    agreement_view_perm_spy.assert_called()
    agreement_add_perm_spy.assert_called()
    agreement_delete_perm_spy.assert_called()

    contact_module_perm_spy.assert_called()
    contact_view_perm_spy.assert_called()
    contact_add_perm_spy.assert_called()
    contact_delete_perm_spy.assert_called()

    email_module_perm_spy.assert_called()
    email_view_perm_spy.assert_called()
    email_add_perm_spy.assert_called()
    email_delete_perm_spy.assert_called()
