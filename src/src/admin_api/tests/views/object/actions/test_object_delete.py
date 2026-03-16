import pytest
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.admin.models import LogEntry, DELETION
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

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


# ----------- Test Permissions and errors


def test_object_delete_action__post_and_patch_not_allowed(staff_client, db):
    agreement = AgreementFactory.create()
    for method in ["post", "patch", "get"]:
        resp = getattr(staff_client, method)(
            f"/api/real_estate/agreement/{agreement.pk}/"
        )
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_object_delete_action__base_permission_check(non_staff_client, db, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement = AgreementFactory.create()
    resp = non_staff_client.delete(f"/api/real_estate/agreement/{agreement.pk}/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_object_delete_action__base_admin_apiview_errors(staff_client, db):
    # Non-existent app
    resp = staff_client.delete("/api/notanapp/agreement/1/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Non-existent model (real_estate app exists)
    resp = staff_client.delete("/api/real_estate/notamodel/1/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Model exists but no admin registered
    resp = staff_client.delete("/api/common/country/1/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}


def test_object_delete_action__delete_permission_required(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    # No permission
    resp = no_perms_staff_client.delete(f"/api/real_estate/agreement/{agreement.pk}/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With delete permission
    delete_perm = Permission.objects.get(codename="delete_agreement")
    no_perms_staff_client.user.user_permissions.set([delete_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.delete(f"/api/real_estate/agreement/{agreement.pk}/")
    assert resp.status_code == status.HTTP_200_OK

    # Verify object was deleted
    assert not Agreement.objects.filter(pk=agreement.pk).exists()


def test_object_delete_action__object_not_found(staff_client):
    resp = staff_client.delete("/api/real_estate/agreement/999999999999/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ----------- Test functionality


def test_object_delete_action__successful_deletion(db, staff_client):
    agreement = AgreementFactory.create()
    agreement_pk = agreement.pk
    obj_repr = str(agreement)

    resp = staff_client.delete(f"/api/real_estate/agreement/{agreement_pk}/")
    assert resp.status_code == status.HTTP_200_OK

    # Check response structure
    assert resp.data == {"messages": [f"The object {obj_repr} was deleted successfully."]}

    # Verify object was actually deleted from database
    assert not Agreement.objects.filter(pk=agreement_pk).exists()


def test_object_delete_action__deletes_cascade_related_objects(db, staff_client):
    agreement = AgreementFactory.create()
    contact1 = ContactFactory.create()
    contact2 = ContactFactory.create()

    # Create commissions that will be CASCADE deleted
    commission1 = AgreementCommission.objects.create(
        agreement=agreement, beneficiary=contact1, value=100.00
    )
    commission2 = AgreementCommission.objects.create(
        agreement=agreement, beneficiary=contact2, value=200.00
    )

    commission1_pk = commission1.pk
    commission2_pk = commission2.pk
    agreement_pk = agreement.pk

    resp = staff_client.delete(f"/api/real_estate/agreement/{agreement_pk}/")
    assert resp.status_code == status.HTTP_200_OK

    # Verify agreement was deleted
    assert not Agreement.objects.filter(pk=agreement_pk).exists()

    # Verify cascade deleted commissions
    assert not AgreementCommission.objects.filter(pk=commission1_pk).exists()
    assert not AgreementCommission.objects.filter(pk=commission2_pk).exists()


def test_object_delete_action__protected_objects_prevent_deletion(db, staff_client):
    # Create a project with a PROTECT relationship
    project = ProjectFactory.create()

    # Create a property that has PROTECT relationship to project
    PropertyFactory.create(project=project)

    resp = staff_client.delete(f"/api/real_estate/project/{project.pk}/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify project was NOT deleted
    assert project.__class__.objects.filter(pk=project.pk).exists()


def test_object_delete_action__perms_needed_prevents_deletion(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    resp = no_perms_staff_client.delete(f"/api/real_estate/agreement/{agreement.pk}/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify agreement was NOT deleted
    assert Agreement.objects.filter(pk=agreement.pk).exists()


def test_object_delete_action__creates_log_entry(db, staff_client):
    agreement = AgreementFactory.create()
    agreement_pk = agreement.pk
    obj_repr = str(agreement)
    content_type = ContentType.objects.get_for_model(agreement)

    # Ensure no log entries exist before deletion
    log_count_before = LogEntry.objects.filter(
        content_type=content_type,
        object_id=str(agreement_pk),
    ).count()

    resp = staff_client.delete(f"/api/real_estate/agreement/{agreement_pk}/")
    assert resp.status_code == status.HTTP_200_OK

    # Check response structure
    assert resp.data == {"messages": [f"The object {obj_repr} was deleted successfully."]}

    # Check that a log entry was created
    log_entries = LogEntry.objects.filter(
        content_type=content_type,
        object_id=str(agreement_pk),
        action_flag=DELETION,
    )

    assert log_entries.count() == log_count_before + 1

    log_entry = log_entries.first()
    assert log_entry.user == staff_client.user
    assert log_entry.object_repr == obj_repr
    assert log_entry.action_flag == DELETION


def test_object_delete_action__all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement_has_delete_permission_spy = mocker.spy(
        AgreementAdmin, "has_delete_permission"
    )
    agreement_get_deleted_objects_spy = mocker.spy(AgreementAdmin, "get_deleted_objects")
    agreement_log_deletion_spy = mocker.spy(AgreementAdmin, "log_deletion")
    agreement_delete_model_spy = mocker.spy(AgreementAdmin, "delete_model")

    agreement = AgreementFactory.create()
    agreement_pk = agreement.pk

    resp = staff_client.delete(f"/api/real_estate/agreement/{agreement_pk}/")
    assert resp.status_code == status.HTTP_200_OK

    admin_site_has_permission_spy.assert_called()
    agreement_has_delete_permission_spy.assert_called()
    agreement_get_deleted_objects_spy.assert_called()
    agreement_log_deletion_spy.assert_called()
    agreement_delete_model_spy.assert_called()


def test_object_delete_action__multiple_different_objects(db, staff_client):
    agreement1 = AgreementFactory.create()
    agreement2 = AgreementFactory.create()

    agreement1_pk = agreement1.pk
    agreement2_pk = agreement2.pk
    obj_repr1 = str(agreement1)
    obj_repr2 = str(agreement2)

    resp1 = staff_client.delete(f"/api/real_estate/agreement/{agreement1_pk}/")
    resp2 = staff_client.delete(f"/api/real_estate/agreement/{agreement2_pk}/")

    assert resp1.status_code == status.HTTP_200_OK
    assert resp2.status_code == status.HTTP_200_OK

    # Should have different messages
    assert obj_repr1 in resp1.data["messages"][0]
    assert obj_repr2 in resp2.data["messages"][0]
    assert resp1.data["messages"][0] != resp2.data["messages"][0]

    # Verify both were deleted
    assert not Agreement.objects.filter(pk=agreement1_pk).exists()
    assert not Agreement.objects.filter(pk=agreement2_pk).exists()


def test_object_delete_action__idempotency_check(db, staff_client):
    agreement = AgreementFactory.create()
    agreement_pk = agreement.pk

    # First deletion should succeed
    resp1 = staff_client.delete(f"/api/real_estate/agreement/{agreement_pk}/")
    assert resp1.status_code == status.HTTP_200_OK

    # Second deletion should return 404 (object not found)
    resp2 = staff_client.delete(f"/api/real_estate/agreement/{agreement_pk}/")
    assert resp2.status_code == status.HTTP_404_NOT_FOUND


def test_object_delete_action__only_deletes_specified_object(db, staff_client):
    agreement1 = AgreementFactory.create()
    agreement2 = AgreementFactory.create()

    agreement1_pk = agreement1.pk
    agreement2_pk = agreement2.pk

    # Delete only agreement1
    resp = staff_client.delete(f"/api/real_estate/agreement/{agreement1_pk}/")
    assert resp.status_code == status.HTTP_200_OK

    # Verify agreement1 was deleted
    assert not Agreement.objects.filter(pk=agreement1_pk).exists()

    # Verify agreement2 still exists
    assert Agreement.objects.filter(pk=agreement2_pk).exists()


def test_object_delete_action__view_permission_not_sufficient(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    # With only view permission
    view_perm = Permission.objects.get(codename="view_agreement")
    no_perms_staff_client.user.user_permissions.set([view_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.delete(f"/api/real_estate/agreement/{agreement.pk}/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify object was NOT deleted
    assert Agreement.objects.filter(pk=agreement.pk).exists()


def test_object_delete_action__change_permission_not_sufficient(
    db, no_perms_staff_client
):
    agreement = AgreementFactory.create()

    # With only change permission
    change_perm = Permission.objects.get(codename="change_agreement")
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.delete(f"/api/real_estate/agreement/{agreement.pk}/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify object was NOT deleted
    assert Agreement.objects.filter(pk=agreement.pk).exists()


def test_object_delete_action__add_permission_not_sufficient(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    # With only add permission
    add_perm = Permission.objects.get(codename="add_agreement")
    no_perms_staff_client.user.user_permissions.set([add_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.delete(f"/api/real_estate/agreement/{agreement.pk}/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify object was NOT deleted
    assert Agreement.objects.filter(pk=agreement.pk).exists()
