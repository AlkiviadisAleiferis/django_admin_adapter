import pytest
from django.contrib import admin
from django.contrib.auth.models import Permission
from rest_framework import status

from admin_api.model_admins import PropertyAdmin
from backend.tests.factories import (
    AgreementFactory,
    ContactFactory,
    UserFactory,
    ProjectFactory,
    PropertyFactory,
)
from backend.real_estate.models import (
    AgreementCommission,
    PropertyOwner,
    PropertyAssociatedContact,
)
from backend.organization.models import User
from django_admin_adapter.utils import get_deleted_objects
from ..utils import get_object_delete_data


# ----------- Test Permissions and errors


def test_object_delete__only_get_allowed(staff_client, db):
    agreement = AgreementFactory.create()
    for method in ["post", "put", "patch", "delete"]:
        resp = getattr(staff_client, method)(
            f"/api/real_estate/agreement/{agreement.pk}/delete/"
        )
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_object_delete__base_permission_check(non_staff_client, db, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement = AgreementFactory.create()
    resp = non_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/delete/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_object_delete__base_admin_apiview_errors(staff_client, db):
    # Non-existent app
    resp = staff_client.get("/api/notanapp/agreement/1/delete/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Non-existent model (real_estate app exists)
    resp = staff_client.get("/api/real_estate/notamodel/1/delete/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Model exists but no admin registered
    resp = staff_client.get("/api/common/country/1/delete/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}


def test_object_delete__view_and_delete_permission_required(db, no_perms_staff_client):
    agreement = AgreementFactory.create()

    # No permission
    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/delete/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With only view permission -
    # should still be forbidden
    view_perm = Permission.objects.get(codename="view_agreement")
    no_perms_staff_client.user.user_permissions.set([view_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )
    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/delete/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With only delete permission -
    # should still be forbidden (needs view too)
    delete_perm = Permission.objects.get(codename="delete_agreement")
    no_perms_staff_client.user.user_permissions.set([delete_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )
    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/delete/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # With both view and delete permissions
    no_perms_staff_client.user.user_permissions.set([view_perm, delete_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )
    resp = no_perms_staff_client.get(f"/api/real_estate/agreement/{agreement.pk}/delete/")
    assert resp.status_code == status.HTTP_200_OK


def test_object_delete__object_not_found(staff_client):
    resp = staff_client.get("/api/real_estate/agreement/999999999999/delete/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ----------- Test functionality


def test_object_delete__simple_object_no_relations(db, staff_client):
    prop = PropertyFactory()
    resp = staff_client.get(f"/api/real_estate/property/{prop.pk}/delete/")
    assert resp.status_code == status.HTTP_200_OK

    expected_structure = get_object_delete_data(staff_client.user, prop)
    assert resp.data["object_repr"] == expected_structure["object_repr"]
    assert resp.data["permissions"] == expected_structure["permissions"]
    assert resp.data["deleted_objects"] == expected_structure["deleted_objects"]
    assert resp.data["model_count"] == expected_structure["model_count"]
    assert resp.data["perms_needed"] == expected_structure["perms_needed"]
    assert resp.data["protected"] == expected_structure["protected"]
    assert resp.data == expected_structure


def test_object_delete__object_with_cascade_relations(db, staff_client):
    prop = PropertyFactory()
    contact1 = ContactFactory.create()
    PropertyOwner.objects.create(property=prop, owner=contact1, percentage=1)
    PropertyAssociatedContact.objects.create(property=prop, contact=contact1)

    resp = staff_client.get(f"/api/real_estate/property/{prop.pk}/delete/")
    assert resp.status_code == status.HTTP_200_OK

    expected_structure = get_object_delete_data(staff_client.user, prop)
    assert resp.data["object_repr"] == expected_structure["object_repr"]
    assert resp.data["permissions"] == expected_structure["permissions"]
    assert resp.data["deleted_objects"] == expected_structure["deleted_objects"]
    assert resp.data["model_count"] == expected_structure["model_count"]
    assert resp.data["perms_needed"] == expected_structure["perms_needed"]
    assert resp.data["protected"] == expected_structure["protected"]
    assert resp.data == expected_structure


def test_object_delete__perms_needed_when_missing_related_delete_permission(
    db, no_perms_staff_client
):
    prop = PropertyFactory()
    contact1 = ContactFactory.create()
    AgreementFactory.create(property=prop)
    PropertyOwner.objects.create(property=prop, owner=contact1, percentage=1)
    PropertyAssociatedContact.objects.create(property=prop, contact=contact1)

    view_perm = Permission.objects.get(codename="view_property")
    delete_perm = Permission.objects.get(codename="delete_property")

    no_perms_staff_client.user.user_permissions.set([view_perm, delete_perm])
    # reload user to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get(f"/api/real_estate/property/{prop.pk}/delete/")
    assert resp.status_code == status.HTTP_200_OK

    expected_structure = get_object_delete_data(no_perms_staff_client.user, prop)
    assert resp.data["object_repr"] == expected_structure["object_repr"]
    assert resp.data["permissions"] == expected_structure["permissions"]
    assert resp.data["deleted_objects"] == expected_structure["deleted_objects"]
    assert resp.data["model_count"] == expected_structure["model_count"]
    assert resp.data["perms_needed"] == expected_structure["perms_needed"]
    assert resp.data["protected"] == expected_structure["protected"]
    assert resp.data == expected_structure


def test_object_delete__all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    property_has_view_permission_spy = mocker.spy(PropertyAdmin, "has_view_permission")
    property_has_delete_permission_spy = mocker.spy(
        PropertyAdmin, "has_delete_permission"
    )

    property = PropertyFactory.create()
    resp = staff_client.get(f"/api/real_estate/property/{property.pk}/delete/")
    assert resp.status_code == status.HTTP_200_OK

    admin_site_has_permission_spy.assert_called()
    property_has_view_permission_spy.assert_called()
    property_has_delete_permission_spy.assert_called()


def test_object_delete__concurrent_requests_same_results(db, staff_client):
    property = PropertyFactory.create()

    resp1 = staff_client.get(f"/api/real_estate/property/{property.pk}/delete/")
    resp2 = staff_client.get(f"/api/real_estate/property/{property.pk}/delete/")

    assert resp1.status_code == status.HTTP_200_OK
    assert resp2.status_code == status.HTTP_200_OK
    assert resp1.data == resp2.data


def test_object_delete__multiple_different_objects(db, staff_client):
    agreement1 = AgreementFactory.create()
    agreement2 = AgreementFactory.create()

    resp1 = staff_client.get(f"/api/real_estate/agreement/{agreement1.pk}/delete/")
    resp2 = staff_client.get(f"/api/real_estate/agreement/{agreement2.pk}/delete/")

    assert resp1.status_code == status.HTTP_200_OK
    assert resp2.status_code == status.HTTP_200_OK

    # Should have different object_repr
    assert resp1.data["object_repr"] == str(agreement1)
    assert resp2.data["object_repr"] == str(agreement2)
    assert resp1.data["object_repr"] != resp2.data["object_repr"]
