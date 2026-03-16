from django_admin_adapter.views.actions import (
    BaseAdminActionAPIView,
    AdminListActionPreviewAPIView,
)
from django.contrib import admin
from django.contrib.auth.models import Permission
from rest_framework import status

from admin_api.model_admins import AgreementAdmin, PropertyAdmin
from backend.tests.factories import AgreementFactory, PropertyFactory


AGREEMENT_ACTION_ENDPOINT = "/api/real_estate/agreement/action/delete_selected/preview/"
PROPERTY_ACTION_ENDPOINT = "/api/real_estate/property/action/delete_selected/preview/"


def test_action_preview_inheritance():
    assert AdminListActionPreviewAPIView.__mro__[1] == BaseAdminActionAPIView


def test_action_preview_only_post_allowed(staff_client):
    for method in ["get", "put", "patch", "delete"]:
        resp = getattr(staff_client, method)(AGREEMENT_ACTION_ENDPOINT)
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_action_preview_base_permission_check(non_staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    resp = non_staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_action_preview_base_admin_apiview_errors(staff_client):
    # Non-existent app
    resp = staff_client.post(
        "/api/notanapp/agreement/action/delete_selected/preview/",
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Non-existent model (real_estate app exists)
    resp = staff_client.post(
        "/api/real_estate/notamodel/action/delete_selected/preview/",
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Model exists but no admin registered (using contact model from common app)
    resp = staff_client.post(
        "/api/common/country/action/delete_selected/preview/",
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}


def test_action_preview_no_objects_selected(db, staff_client):
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    # Should fail with different error (no objects selected)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["No objects were selected."]}


def test_action_preview_no_data_provided(db, staff_client):
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        format="json",
    )
    # Should fail with different error (no objects selected)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["No objects were selected."]}


def test_action_preview_non_existent_action(db, staff_client):
    agreement = AgreementFactory.create()
    resp = staff_client.post(
        "/api/real_estate/agreement/action/non_existent_action/preview/",
        data={"select_across": 0, "selected_objects": [agreement.id]},
        format="json",
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_action_preview_malformed_data(db, staff_client):
    # Test malformed data (not a dict)
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data=[],
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["Malformed data provided (1)."]}

    # Test selected_objects not a list
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": "not a list"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["Malformed data provided (2)."]}

    # Test invalid select_across value
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": "invalid", "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["Malformed data provided (3)."]}

    # Test invalid pk type in selected_objects
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": [{"invalid": "object"}]},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["Malformed data provided (4)."]}


def test_action_preview_delete_selected_single_object(db, staff_client):
    property1 = PropertyFactory.create()
    resp = staff_client.post(
        PROPERTY_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": [property1.id]},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["name"] == "Delete selected objects"
    assert set(str(x) for x in resp.data["deletable_objects"]) == {
        f'<a href="/real_estate/property/{property1.id}/">{property1}</a>'
    }
    assert resp.data["model_count"] == {"Properties": "1"}
    assert resp.data["description"] == "Delete selected objects"
    assert resp.data["perms_needed"] == ()
    assert resp.data["protected"] == ()

    # now protected
    property2 = PropertyFactory.create()
    agreement = AgreementFactory.create(property=property2)
    resp = staff_client.post(
        PROPERTY_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": [property2.id]},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["name"] == "Delete selected objects"
    assert set(str(x) for x in resp.data["deletable_objects"]) == {
        f'<a href="/real_estate/property/{property2.id}/">{property2}</a>'
    }
    assert resp.data["model_count"] == {"Properties": "1"}
    assert resp.data["description"] == "Delete selected objects"
    assert resp.data["perms_needed"] == ()
    assert [str(x) for x in resp.data["protected"]] == [
        f'<a href="/real_estate/agreement/{agreement.id}/">{agreement}</a>'
    ]


def test_action_preview_delete_selected_no_delete_permission(db, no_perms_staff_client):
    change_perm = Permission.objects.get(codename="change_property")
    no_perms_staff_client.user.user_permissions.add(change_perm)

    property3 = PropertyFactory.create()
    AgreementFactory.create(property=property3)

    resp = no_perms_staff_client.post(
        PROPERTY_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": [property3.id]},
        format="json",
    )
    # action will not be found
    # because delete permission is missing
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_action_preview_delete_selected_multiple_objects(db, staff_client):
    property1 = PropertyFactory.create()
    property2 = PropertyFactory.create()
    property3 = PropertyFactory.create()

    resp = staff_client.post(
        PROPERTY_ACTION_ENDPOINT,
        data={
            "select_across": 0,
            "selected_objects": [property1.id, property2.id, property3.id],
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["name"] == "Delete selected objects"
    assert resp.data["model_count"] == {"Properties": "3"}
    assert set(str(x) for x in resp.data["deletable_objects"]) == {
        f'<a href="/real_estate/property/{property1.id}/">{property1}</a>',
        f'<a href="/real_estate/property/{property2.id}/">{property2}</a>',
        f'<a href="/real_estate/property/{property3.id}/">{property3}</a>',
    }
    assert resp.data["description"] == "Delete selected objects"
    assert resp.data["perms_needed"] == ()
    assert resp.data["protected"] == ()

    # now protected
    agreement = AgreementFactory.create(property=property2)
    resp = staff_client.post(
        PROPERTY_ACTION_ENDPOINT,
        data={
            "select_across": 0,
            "selected_objects": [property1.id, property2.id, property3.id],
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["name"] == "Delete selected objects"
    assert resp.data["model_count"] == {"Properties": "3"}
    assert set(str(x) for x in resp.data["deletable_objects"]) == {
        f'<a href="/real_estate/property/{property1.id}/">{property1}</a>',
        f'<a href="/real_estate/property/{property2.id}/">{property2}</a>',
        f'<a href="/real_estate/property/{property3.id}/">{property3}</a>',
    }
    assert resp.data["description"] == "Delete selected objects"
    assert resp.data["perms_needed"] == ()
    assert [str(x) for x in resp.data["protected"]] == [
        f'<a href="/real_estate/agreement/{agreement.id}/">{agreement}</a>'
    ]


def test_action_preview_delete_selected_select_across(db, staff_client):
    # Create multiple properties
    property1 = PropertyFactory.create()
    property2 = PropertyFactory.create()
    property3 = PropertyFactory.create()

    resp = staff_client.post(
        PROPERTY_ACTION_ENDPOINT,
        data={"select_across": 1, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["name"] == "Delete selected objects"
    assert resp.data["description"] == "Delete selected objects"
    assert set(resp.data["deletable_objects"]) == {
        f'<a href="/real_estate/property/{property1.id}/">{property1}</a>',
        f'<a href="/real_estate/property/{property2.id}/">{property2}</a>',
        f'<a href="/real_estate/property/{property3.id}/">{property3}</a>',
    }
    assert resp.data["model_count"] == {"Properties": "3"}
    assert resp.data["perms_needed"] == ()
    assert resp.data["protected"] == ()


def test_action_preview_custom_action(db, staff_client):
    # with multiple selected objects
    agreement1 = AgreementFactory.create()
    agreement2 = AgreementFactory.create()
    resp = staff_client.post(
        "/api/real_estate/agreement/action/test_action/preview/",
        data={"select_across": 0, "selected_objects": [agreement1.id, agreement2.id]},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["name"] == "Test action"
    assert resp.data["description"] == "Test the actions template to see this description"

    # with select across
    agreement1 = AgreementFactory.create()
    agreement2 = AgreementFactory.create()
    resp = staff_client.post(
        "/api/real_estate/agreement/action/test_action/preview/",
        data={"select_across": 1, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["name"] == "Test action"
    assert resp.data["description"] == "Test the actions template to see this description"


def test_action_preview_with_string_pks(db, staff_client):
    agreement = AgreementFactory.create()
    resp = staff_client.post(
        "/api/real_estate/agreement/action/test_action/preview/",
        data={"select_across": 0, "selected_objects": [str(agreement.id)]},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["name"] == "Test action"
    assert resp.data["description"] == "Test the actions template to see this description"


def test_action_preview_with_mixed_pk_types(db, staff_client):
    agreement1 = AgreementFactory.create()
    agreement2 = AgreementFactory.create()
    resp = staff_client.post(
        "/api/real_estate/agreement/action/test_action/preview/",
        data={
            "select_across": 0,
            "selected_objects": [agreement1.id, str(agreement2.id)],
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["name"] == "Test action"
    assert resp.data["description"] == "Test the actions template to see this description"


def test_action_preview_incorrect_lookup_parameters(db, staff_client):
    agreement = AgreementFactory.create()
    # Using invalid query parameters
    # that would cause IncorrectLookupParameters
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT + "?invalid_lookup=bad",
        data={"select_across": 0, "selected_objects": [agreement.id]},
        format="json",
    )
    # This should be caught and return 403
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_action_preview_all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement_has_change_permission_spy = mocker.spy(
        AgreementAdmin, "has_change_permission"
    )
    agreement_get_actions_spy = mocker.spy(AgreementAdmin, "get_actions")
    agreement_get_changelist_spy = mocker.spy(AgreementAdmin, "get_changelist_instance")
    agreement_test_action_spy = mocker.spy(AgreementAdmin, "test_action")

    agreement = AgreementFactory.create()
    resp = staff_client.post(
        "/api/real_estate/agreement/action/test_action/preview/",
        data={"select_across": 0, "selected_objects": [agreement.id]},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK

    admin_site_has_permission_spy.assert_called()
    agreement_has_change_permission_spy.assert_called()
    agreement_get_actions_spy.assert_called()
    agreement_get_changelist_spy.assert_called()
    agreement_test_action_spy.assert_called()


def test_action_preview_empty_queryset_after_filter(db, staff_client):
    # Create an agreement but try to preview with a non-existent ID
    AgreementFactory.create()
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": [99999]},
        format="json",
    )
    # Should still return 200 with empty deletable_objects
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["name"] == "Delete selected objects"
