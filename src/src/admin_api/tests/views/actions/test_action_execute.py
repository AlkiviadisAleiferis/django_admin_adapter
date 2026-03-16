import pytest

from django.contrib import admin
from django.contrib.admin.utils import model_ngettext
from django.contrib.auth.models import Permission
from rest_framework import status

from admin_api.model_admins import AgreementAdmin
from backend.tests.factories import AgreementFactory, ContactFactory
from backend.real_estate.models import Agreement
from backend.common.models import Contact
from backend.organization.models import User


AGREEMENT_ACTION_ENDPOINT = "/api/real_estate/agreement/action/delete_selected/execute/"
CONTACT_ACTION_ENDPOINT = "/api/common/contact/action/delete_selected/execute/"


def test_action_execute_only_post_allowed(staff_client):
    for method in ["get", "put", "patch", "delete"]:
        resp = getattr(staff_client, method)(AGREEMENT_ACTION_ENDPOINT)
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_action_execute_base_permission_check(non_staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    resp = non_staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_action_execute_base_admin_apiview_errors(staff_client, no_perms_staff_client):
    # Non-existent app
    resp = staff_client.post(
        "/api/notanapp/agreement/action/delete_selected/execute/",
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Non-existent model (real_estate app exists)
    resp = staff_client.post(
        "/api/real_estate/notamodel/action/delete_selected/execute/",
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Model exists but no admin registered
    resp = staff_client.post(
        "/api/common/country/action/delete_selected/execute/",
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}

    # No permission
    resp = no_perms_staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_action_execute_delete_selected_no_objects(db, staff_client):
    # No permission
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["No objects were selected."]}


def test_action_execute_non_existent_action(db, staff_client):
    agreement = AgreementFactory.create()
    resp = staff_client.post(
        "/api/real_estate/agreement/action/non_existent_action/execute/",
        data={"select_across": 0, "selected_objects": [agreement.id]},
        format="json",
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_action_execute_malformed_data(db, staff_client):
    # Test malformed data (not a dict)
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data="not a dict",
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


def test_action_execute_no_objects_selected(db, staff_client):
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["No objects were selected."]}


def test_action_execute_delete_selected_single_object(db, staff_client):
    agreement = AgreementFactory.create()
    agreement_id = agreement.id

    # Verify object exists
    assert Agreement.objects.filter(id=agreement_id).exists()

    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": [agreement_id]},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {
        "messages": [
            f"Successfully deleted {1} {model_ngettext(Agreement._meta, 1).capitalize()}."
        ]
    }

    # Verify object was deleted
    assert not Agreement.objects.filter(id=agreement_id).exists()


def test_action_execute_delete_selected_multiple_objects(db, staff_client):
    agreement1 = AgreementFactory.create()
    agreement2 = AgreementFactory.create()
    agreement3 = AgreementFactory.create()

    ids = [agreement1.id, agreement2.id, agreement3.id]

    # Verify objects exist
    assert Agreement.objects.filter(id__in=ids).count() == 3

    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={
            "select_across": 0,
            "selected_objects": ids,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {
        "messages": [
            f"Successfully deleted {3} {model_ngettext(Agreement._meta, 3).capitalize()}."
        ]
    }

    # Verify objects were deleted
    assert not Agreement.objects.filter(id__in=ids).exists()


def test_action_execute_delete_selected_select_across(db, staff_client):
    # Create multiple agreements
    AgreementFactory.create_batch(5)

    initial_count = Agreement.objects.count()
    assert initial_count == 5

    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 1, "selected_objects": []},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {
        "messages": [
            f"Successfully deleted {5} {model_ngettext(Agreement._meta, 5).capitalize()}."
        ]
    }

    # Verify all objects were deleted
    assert Agreement.objects.count() == 0


def test_action_execute_custom_action(db, staff_client):
    agreement = AgreementFactory.create()
    resp = staff_client.post(
        "/api/real_estate/agreement/action/test_action/execute/",
        data={"select_across": 0, "selected_objects": [agreement.id]},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "messages" in resp.data
    assert resp.data["messages"] == ["test action executed successfully."]


def test_action_execute_with_string_pks(db, staff_client):
    agreement = AgreementFactory.create()
    agreement_id = agreement.id

    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": [str(agreement_id)]},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {
        "messages": [
            f"Successfully deleted {1} {model_ngettext(Agreement._meta, 1).capitalize()}."
        ]
    }

    # Verify object was deleted
    assert not Agreement.objects.filter(id=agreement_id).exists()


def test_action_execute_with_mixed_pk_types(db, staff_client):
    """Test that mixed int and string PKs are accepted."""
    agreement1 = AgreementFactory.create()
    agreement2 = AgreementFactory.create()
    ids = [agreement1.id, agreement2.id]

    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={
            "select_across": 0,
            "selected_objects": [agreement1.id, str(agreement2.id)],
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {
        "messages": [
            f"Successfully deleted {2} {model_ngettext(Agreement._meta, 2).capitalize()}."
        ]
    }

    # Verify objects were deleted
    assert Agreement.objects.filter(id__in=ids).count() == 0


def test_action_execute_incorrect_lookup_parameters(db, staff_client):
    agreement = AgreementFactory.create()

    # Using invalid query parameters that would cause IncorrectLookupParameters
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT + "?invalid_lookup=bad",
        data={"select_across": 0, "selected_objects": [agreement.id]},
        format="json",
    )
    # This should be caught and return 403
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Verify object was NOT deleted
    assert Agreement.objects.filter(id=agreement.id).exists()


def test_action_execute_all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement_has_change_permission_spy = mocker.spy(
        AgreementAdmin, "has_change_permission"
    )
    agreement_get_actions_spy = mocker.spy(AgreementAdmin, "get_actions")
    agreement_get_changelist_spy = mocker.spy(AgreementAdmin, "get_changelist_instance")
    agreement_log_deletion_spy = mocker.spy(AgreementAdmin, "log_deletion")
    agreement_delete_queryset_spy = mocker.spy(AgreementAdmin, "delete_queryset")

    agreement = AgreementFactory.create()
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": [agreement.id]},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK

    admin_site_has_permission_spy.assert_called()
    agreement_has_change_permission_spy.assert_called()
    agreement_get_actions_spy.assert_called()
    agreement_get_changelist_spy.assert_called()
    agreement_log_deletion_spy.assert_called()
    agreement_delete_queryset_spy.assert_called()


def test_action_execute_with_contact_model(db, staff_client):
    contact = ContactFactory.create()
    contact_id = contact.id

    # Verify object exists
    assert Contact.objects.filter(id=contact_id).exists()

    resp = staff_client.post(
        CONTACT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": [contact_id]},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "messages" in resp.data
    assert "Successfully deleted 1" in resp.data["messages"][0]

    # Verify object was deleted
    assert not Contact.objects.filter(id=contact_id).exists()


def test_action_execute_empty_queryset_after_filter(db, staff_client):
    # Create an agreement but try to execute with a non-existent ID
    AgreementFactory.create()
    initial_count = Agreement.objects.count()

    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": [99999]},
        format="json",
    )
    # Should return 400 because no objects to perform action on
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["No objects to perform action on."]}

    # Verify no objects were deleted
    assert Agreement.objects.count() == initial_count


def test_action_execute_delete_selected_with_no_delete_permission(
    db, no_perms_staff_client
):
    change_perm = Permission.objects.get(codename="change_agreement")
    view_perm = Permission.objects.get(codename="view_agreement")
    add_perm = Permission.objects.get(codename="add_agreement")
    # Give all perms exept delete
    no_perms_staff_client.user.user_permissions.set([change_perm, view_perm, add_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    agreement = AgreementFactory.create()
    agreement_id = agreement.id

    resp = no_perms_staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={"select_across": 0, "selected_objects": [agreement_id]},
        format="json",
    )
    # Should return 404 because the user
    # doesn't have permission to access this action
    assert resp.status_code == status.HTTP_404_NOT_FOUND

    # Verify object was NOT deleted
    assert Agreement.objects.filter(id=agreement_id).exists()


def test_action_execute_preserves_other_objects(db, staff_client):
    agreement1 = AgreementFactory.create()
    agreement2 = AgreementFactory.create()
    agreement3 = AgreementFactory.create()

    # Delete only agreement1 and agreement2
    resp = staff_client.post(
        AGREEMENT_ACTION_ENDPOINT,
        data={
            "select_across": 0,
            "selected_objects": [agreement1.id, agreement2.id],
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {
        "messages": [
            f"Successfully deleted {2} {model_ngettext(Agreement._meta, 2).capitalize()}."
        ]
    }

    # Verify only selected objects were deleted
    assert not Agreement.objects.filter(id=agreement1.id).exists()
    assert not Agreement.objects.filter(id=agreement2.id).exists()
    assert Agreement.objects.filter(id=agreement3.id).exists()
