import pytest

from django.contrib import admin
from django.contrib.auth.models import Permission
from rest_framework import status

from .utils import AGREEMENT_LIST_INFO_DATA

from admin_api.model_admins import AgreementAdmin
from backend.organization.models import User


def test_list_info_only_only_get_allowed(staff_client):
    for method in ["post", "put", "patch", "delete"]:
        resp = getattr(staff_client, method)("/api/common/contact/info/")
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_list_info_base_permission_check(non_staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    resp = non_staff_client.get("/api/common/contact/info/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_list_info_base_admin_apiview_errors(api_rf, staff_client):
    resp = staff_client.get("/api/notanapp/contact/info/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    resp = staff_client.get("/api/common/notamodel/info/")  # common app exists
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    resp = staff_client.get("/api/common/country/info/")  # country model exists
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}


def test_list_info_no_change_or_view_parmission(db, no_perms_staff_client):
    view_perm = Permission.objects.get(codename="view_contact")
    change_perm = Permission.objects.get(codename="change_contact")

    resp = no_perms_staff_client.get("/api/common/contact/info/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # only view permission
    no_perms_staff_client.user.user_permissions.set([view_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get("/api/common/contact/info/")
    assert resp.status_code == status.HTTP_200_OK

    # only change permission
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get("/api/common/contact/info/")
    assert resp.status_code == status.HTTP_200_OK


def test_list_info_incorrect_lookup(db, staff_client):
    resp = staff_client.get("/api/common/contact/info/?wrong_lookup_parameter=invalid")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"message": "Incorrect parameters used in URL."}


def test_list_info_expected_structure(db, staff_client):
    resp = staff_client.get("/api/real_estate/agreement/info/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == AGREEMENT_LIST_INFO_DATA


def test_all_the_proper_methods_called(staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")

    agreement_view_perm_spy = mocker.spy(AgreementAdmin, "has_view_permission")
    agreement_has_view_or_change_permission_spy = mocker.spy(
        AgreementAdmin, "has_view_or_change_permission"
    )
    agreement_action_choices_spy = mocker.spy(AgreementAdmin, "get_action_choices")
    agreement_actions_spy = mocker.spy(AgreementAdmin, "get_actions")
    agreement_get_list_filter_spy = mocker.spy(AgreementAdmin, "get_list_filter")

    resp = staff_client.get("/api/real_estate/agreement/info/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == AGREEMENT_LIST_INFO_DATA

    admin_site_has_permission_spy.assert_called()

    agreement_view_perm_spy.assert_called()
    agreement_has_view_or_change_permission_spy.assert_called()
    agreement_action_choices_spy.assert_called()
    agreement_actions_spy.assert_called()
    agreement_get_list_filter_spy.assert_called()
