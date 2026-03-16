import pytest
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from admin_api.model_admins import AgreementAdmin
from backend.tests.factories import (
    AgreementFactory,
    EmailFactory,
    UserFactory,
    ProjectFactory,
)
from backend.real_estate.models import Agreement
from backend.organization.models import User
from django_admin_adapter.views.history import PAGE_VAR
from ..utils import get_object_history_data, DummyRequest


# ----------- Test Permissions and errors


def test_object_history__only_get_allowed(staff_client, db):
    agreement = AgreementFactory.create()
    for method in ["post", "put", "patch", "delete"]:
        resp = getattr(staff_client, method)(
            f"/api/real_estate/agreement/{agreement.pk}/history/"
        )
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_object_history__base_permission_check(non_staff_client, db, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement = AgreementFactory.create()
    resp = non_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/history/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_object_history__base_admin_apiview_errors(staff_client, db):
    # Non-existent app
    resp = staff_client.get("/api/notanapp/agreement/1/history/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Non-existent model (real_estate app exists)
    resp = staff_client.get("/api/real_estate/notamodel/1/history/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Model exists but no admin registered
    resp = staff_client.get("/api/common/country/1/history/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}


def test_object_history__permissions(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    # No permission
    resp = no_perms_staff_client.get(
        f"/api/real_estate/agreement/{agreement.pk}/history/"
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With view permission
    view_perm = Permission.objects.get(codename="view_agreement")
    no_perms_staff_client.user.user_permissions.set([view_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )
    resp = no_perms_staff_client.get(
        f"/api/real_estate/agreement/{agreement.pk}/history/"
    )
    assert resp.status_code == status.HTTP_200_OK

    # With change permission (should also work)
    change_perm = Permission.objects.get(codename="change_agreement")
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )
    resp = no_perms_staff_client.get(
        f"/api/real_estate/agreement/{agreement.pk}/history/"
    )
    assert resp.status_code == status.HTTP_200_OK

    # With view permission
    # BUT no permissino provided
    # by `has_history_permission` method
    email = EmailFactory.create()
    view_perm = Permission.objects.get(codename="view_email")
    no_perms_staff_client.user.user_permissions.set([view_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )
    resp = no_perms_staff_client.get(f"/api/common/email/{email.pk}/history/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With only delete permission - should be forbidden
    delete_perm = Permission.objects.get(codename="delete_agreement")
    no_perms_staff_client.user.user_permissions.set([delete_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )
    resp = no_perms_staff_client.get(
        f"/api/real_estate/agreement/{agreement.pk}/history/"
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With only add permission - should be forbidden
    add_perm = Permission.objects.get(codename="add_agreement")
    no_perms_staff_client.user.user_permissions.set([add_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )
    resp = no_perms_staff_client.get(
        f"/api/real_estate/agreement/{agreement.pk}/history/"
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_object_history__object_not_found(staff_client):
    resp = staff_client.get("/api/real_estate/agreement/999999999999/history/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ----------- Test functionality


def test_object_history__structure(db, staff_client, settings_no_tz):
    request = DummyRequest(staff_client.user)

    agreement = AgreementFactory.create()
    agreement_admin = admin.site._registry[Agreement]

    # create entries
    agreement_admin.log_addition(request, agreement, "Addition")
    agreement_admin.log_change(request, agreement, "Change")
    agreement_admin.log_deletion(request, agreement, "Deletion")

    # with no page var, the first is provided
    resp = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/history/")
    assert resp.status_code == status.HTTP_200_OK

    expected_data = get_object_history_data(agreement, page_num=1)
    assert resp.data["object_repr"] == expected_data["object_repr"]
    assert resp.data["data"]["results"] == expected_data["data"]["results"]
    assert resp.data["data"]["page"] == expected_data["data"]["page"]
    assert resp.data["data"]["total_pages"] == expected_data["data"]["total_pages"]
    assert (
        resp.data["data"]["total_objects_num"]
        == expected_data["data"]["total_objects_num"]
    )
    assert resp.data["data"] == expected_data["data"]

    resp = staff_client.get(
        f"/api/real_estate/agreement/{agreement.pk}/history/?{PAGE_VAR}=1"
    )
    assert resp.status_code == status.HTTP_200_OK
    expected_data = get_object_history_data(agreement, page_num=1)
    assert resp.data == expected_data


def test_object_history__empty_history(db, staff_client):
    agreement = AgreementFactory.create()

    resp = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/history/")
    assert resp.status_code == status.HTTP_200_OK

    # Should have empty results
    assert resp.data == {
        "object_repr": str(agreement),
        "data": {
            "results": [],
            "total_objects_num": 0,
            "page": 1,
            "total_pages": 1,
        },
    }


def test_object_history__second_page(db, staff_client, settings_no_tz):
    request = DummyRequest(staff_client.user)

    agreement = AgreementFactory.create()
    agreement_admin = admin.site._registry[Agreement]

    # create entries
    agreement_admin.log_addition(request, agreement, "Addition")
    for i in range(30):
        agreement_admin.log_change(request, agreement, f"Change {i}")
    agreement_admin.log_deletion(request, agreement, "Deletion")

    # with no page var, the first is provided
    resp = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/history/")
    assert resp.status_code == status.HTTP_200_OK

    expected_data = get_object_history_data(agreement, page_num=1)
    assert resp.data["object_repr"] == expected_data["object_repr"]
    assert resp.data["data"]["results"] == expected_data["data"]["results"]
    assert resp.data["data"]["page"] == expected_data["data"]["page"]
    assert resp.data["data"]["total_pages"] == expected_data["data"]["total_pages"]
    assert (
        resp.data["data"]["total_objects_num"]
        == expected_data["data"]["total_objects_num"]
    )
    assert resp.data["data"] == expected_data["data"]

    # with page var, the second is provided
    resp = staff_client.get(
        f"/api/real_estate/agreement/{agreement.pk}/history/?{PAGE_VAR}=2"
    )
    assert resp.status_code == status.HTTP_200_OK
    expected_data = get_object_history_data(agreement, page_num=2)

    assert resp.data["object_repr"] == expected_data["object_repr"]
    assert resp.data["data"]["results"] == expected_data["data"]["results"]
    assert resp.data["data"]["page"] == expected_data["data"]["page"]
    assert resp.data["data"]["total_pages"] == expected_data["data"]["total_pages"]
    assert (
        resp.data["data"]["total_objects_num"]
        == expected_data["data"]["total_objects_num"]
    )
    assert resp.data["data"] == expected_data["data"]


def test_object_history__all_log_entries_present(db, staff_client, settings_no_tz):
    request = DummyRequest(staff_client.user)

    agreement = AgreementFactory.create()
    agreement_admin = admin.site._registry[Agreement]

    # create entries
    agreement_admin.log_addition(request, agreement, "Addition")
    for i in range(10):
        agreement_admin.log_change(request, agreement, f"Change {i}")
    agreement_admin.log_deletion(request, agreement, "Deletion")

    # with no page var, the first is provided
    resp = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/history/")
    assert resp.status_code == status.HTTP_200_OK

    expected_data = get_object_history_data(agreement, page_num=1)
    log_entries = LogEntry.objects.filter(object_id=agreement.pk)
    assert len(log_entries) == 12
    assert expected_data["data"]["total_objects_num"] == 12

    for log_entry in log_entries:
        for log_entry_data in expected_data["data"]["results"]:
            if log_entry_data["description"] == log_entry.change_message:
                break
        else:
            assert False


def test_object_history__pagination_invalid_page_number(db, staff_client, settings_no_tz):
    request = DummyRequest(staff_client.user)

    agreement = AgreementFactory.create()
    agreement_admin = admin.site._registry[Agreement]

    # create entries
    agreement_admin.log_addition(request, agreement, "Addition")

    for i in range(30):
        agreement_admin.log_change(request, agreement, f"Change {i}")
    agreement_admin.log_deletion(request, agreement, "Deletion")

    expected_data = get_object_history_data(agreement, page_num=1)

    # for invalid page choices, the result is always the first page
    for page_var_value in (-1, "inv", 0, 1000, 2.3):
        resp = staff_client.get(
            f"/api/real_estate/agreement/{agreement.pk}/history/?{PAGE_VAR}={page_var_value}"
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data == expected_data


def test_object_history__all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement_has_view_or_change_permission_spy = mocker.spy(
        AgreementAdmin, "has_view_or_change_permission"
    )

    agreement = AgreementFactory.create()
    resp = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/history/")
    assert resp.status_code == status.HTTP_200_OK

    admin_site_has_permission_spy.assert_called()
    agreement_has_view_or_change_permission_spy.assert_called()


def test_object_history__concurrent_requests_same_results(db, staff_client):
    request = DummyRequest(staff_client.user)

    agreement = AgreementFactory.create()
    agreement_admin = admin.site._registry[Agreement]

    # create entries
    agreement_admin.log_addition(request, agreement, "Addition")
    agreement_admin.log_change(request, agreement, "Change")
    agreement_admin.log_deletion(request, agreement, "Deletion")

    resp1 = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/history/")
    resp2 = staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/history/")

    assert resp1.status_code == status.HTTP_200_OK
    assert resp2.status_code == status.HTTP_200_OK
    assert resp1.data == resp2.data


def test_object_history__only_shows_logs_for_specific_object(
    db, staff_client, settings_no_tz
):
    request = DummyRequest(staff_client.user)

    agreement1 = AgreementFactory.create()
    agreement2 = AgreementFactory.create()
    agreement_admin = admin.site._registry[Agreement]

    # create entries 1
    agreement_admin.log_addition(request, agreement1, "Addition")
    agreement_admin.log_change(request, agreement1, "Change")
    agreement_admin.log_deletion(request, agreement1, "Deletion")
    # create entries 2
    agreement_admin.log_addition(request, agreement2, "Addition")
    agreement_admin.log_change(request, agreement2, "Change")
    agreement_admin.log_deletion(request, agreement2, "Deletion")

    # Request history for agreement1
    resp = staff_client.get(f"/api/real_estate/agreement/{agreement1.pk}/history/")
    assert resp.status_code == status.HTTP_200_OK
    expected_data = get_object_history_data(agreement1, page_num=1)

    # Should only have 1 log entry (for agreement1)
    assert resp.data == expected_data
    assert resp.data["data"]["total_objects_num"] == 3
