import pytest

from django.contrib import admin
from django.contrib.auth.models import Permission
from rest_framework import status

from admin_api.user import UserAdmin
from backend.organization.models import User
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY


def test_password_change_only_post_allowed(staff_client):
    for method in ["get", "put", "patch", "delete"]:
        resp = getattr(staff_client, method)("/api/password_change/")
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_password_change_base_permission_check(non_staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    resp = non_staff_client.post(
        "/api/password_change/",
        data={
            "old_password": "1234",
            "new_password1": "newpass123",
            "new_password2": "newpass123",
        },
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_password_change_user_admin_not_registered(staff_client, mocker):
    # Mock the registry to return None for User model
    # Temporarily remove User from registry
    if User in admin.site._registry:
        user_admin = admin.site._registry.pop(User)

    try:
        resp = staff_client.post(
            "/api/password_change/",
            data={
                "old_password": "1234",
                "new_password1": "newpass123",
                "new_password2": "newpass123",
            },
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
    finally:
        # Restore the registry
        if User not in admin.site._registry:
            admin.site._registry[User] = user_admin


def test_password_change_user_has_no_change_permission(db, no_perms_staff_client, mocker):
    # Mock has_change_permission to return False
    mocker.patch.object(UserAdmin, "has_change_permission", return_value=False)

    resp = no_perms_staff_client.post(
        "/api/password_change/",
        data={
            "old_password": "1234",
            "new_password1": "newpass123",
            "new_password2": "newpass123",
        },
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_password_change_get_object_returns_none(db, staff_client, mocker):
    # Mock get_object to return None
    mocker.patch.object(UserAdmin, "get_object", return_value=None)

    resp = staff_client.post(
        "/api/password_change/",
        data={
            "old_password": "1234",
            "new_password1": "newpass123",
            "new_password2": "newpass123",
        },
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_password_change_missing_old_password(db, staff_client):
    resp = staff_client.post(
        "/api/password_change/",
        data={
            "new_password1": "newpass123",
            "new_password2": "newpass123",
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {
        "error_data": {
            "old_password": [{"message": "The old password must be provided."}]
        }
    }


def test_password_change_empty_old_password(db, staff_client):
    resp = staff_client.post(
        "/api/password_change/",
        data={
            "old_password": "",
            "new_password1": "newpass123",
            "new_password2": "newpass123",
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {
        "error_data": {
            "old_password": [{"message": "The old password must be provided."}]
        }
    }


def test_password_change_incorrect_old_password(db, staff_client):
    data = {
        "old_password": "wrongpassword",
        "password1": "newpass123",
        "password2": "newpass123",
    }
    resp = staff_client.post(
        "/api/password_change/",
        data=encode_multipart(data=data, boundary=BOUNDARY),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {
        "error_data": {"old_password": [{"message": "The password is incorrect."}]}
    }


def test_password_change_new_passwords_dont_match(db, staff_client):
    data = {
        "old_password": "1234",
        "password1": "newpass123",
        "password2": "newpass1234",
    }
    resp = staff_client.post(
        "/api/password_change/",
        data=encode_multipart(data=data, boundary=BOUNDARY),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {
        "error_data": {
            "password2": [
                {
                    "message": "The two password fields didn’t match.",
                    "code": "password_mismatch",
                }
            ]
        }
    }


def test_password_change_new_password_validation(db, staff_client):
    data = {
        "old_password": "1234",
        "password1": "12",
        "password2": "12",
    }
    resp = staff_client.post(
        "/api/password_change/",
        data=encode_multipart(data=data, boundary=BOUNDARY),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {
        "error_data": {
            "password2": [
                {
                    "message": "This password is too short. It must contain at least 8 characters.",
                    "code": "password_too_short",
                },
                {
                    "message": "This password is too common.",
                    "code": "password_too_common",
                },
                {
                    "message": "This password is entirely numeric.",
                    "code": "password_entirely_numeric",
                },
            ]
        }
    }


def test_password_change_successful(db, staff_client):
    data = {
        "old_password": "1234",
        "password1": "NewSecurePass123!",
        "password2": "NewSecurePass123!",
    }
    user = staff_client.user
    old_password_hash = user.password

    resp = staff_client.post(
        "/api/password_change/",
        data=encode_multipart(data=data, boundary=BOUNDARY),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_200_OK

    # Verify password was actually changed
    user.refresh_from_db()
    assert user.password != old_password_hash
    assert user.check_password("NewSecurePass123!")
    assert not user.check_password("1234")


def test_password_change_missing_new_password1(db, staff_client):
    data = {
        "old_password": "1234",
        "password2": "Newpass!123",
    }
    resp = staff_client.post(
        "/api/password_change/",
        data=encode_multipart(data=data, boundary=BOUNDARY),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {
        "error_data": {
            "password1": [{"message": "This field is required.", "code": "required"}],
        }
    }


def test_password_change_missing_new_password2(db, staff_client):
    data = {
        "old_password": "1234",
        "password1": "Newpass!123",
    }
    resp = staff_client.post(
        "/api/password_change/",
        data=encode_multipart(data=data, boundary=BOUNDARY),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {
        "error_data": {
            "password2": [{"message": "This field is required.", "code": "required"}],
        }
    }


def test_password_change_all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    user_get_object_spy = mocker.spy(UserAdmin, "get_object")
    user_has_change_permission_spy = mocker.spy(UserAdmin, "has_change_permission")
    user_construct_change_message_spy = mocker.spy(UserAdmin, "construct_change_message")
    user_log_change_spy = mocker.spy(UserAdmin, "log_change")

    resp = staff_client.post(
        "/api/password_change/",
        data=encode_multipart(
            data={
                "old_password": "1234",
                "password1": "NewSecurePass123!",
                "password2": "NewSecurePass123!",
            },
            boundary=BOUNDARY,
        ),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_200_OK

    admin_site_has_permission_spy.assert_called()
    user_get_object_spy.assert_called()
    user_has_change_permission_spy.assert_called()
    user_construct_change_message_spy.assert_called()
    user_log_change_spy.assert_called()


def test_password_change_logs_change_in_admin(db, staff_client):
    from django.contrib.admin.models import LogEntry, CHANGE

    user = staff_client.user
    initial_log_count = LogEntry.objects.filter(
        user_id=user.id, object_id=str(user.id), action_flag=CHANGE
    ).count()

    resp = staff_client.post(
        "/api/password_change/",
        data=encode_multipart(
            data={
                "old_password": "1234",
                "password1": "NewSecurePass123!",
                "password2": "NewSecurePass123!",
            },
            boundary=BOUNDARY,
        ),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_200_OK

    # Verify a new log entry was created
    final_log_count = LogEntry.objects.filter(
        user_id=user.id, object_id=str(user.id), action_flag=CHANGE
    ).count()
    assert final_log_count == initial_log_count + 1

    # Verify the log entry mentions password change
    latest_log = LogEntry.objects.filter(
        user_id=user.id, object_id=str(user.id), action_flag=CHANGE
    ).latest("action_time")
    assert "password" in latest_log.change_message.lower()


def test_password_change_only_change_perm_needed(db, no_perms_staff_client):
    change_perm = Permission.objects.get(codename="change_user")
    user = no_perms_staff_client.user
    old_password_hash = user.password

    resp = no_perms_staff_client.post(
        "/api/password_change/",
        data=encode_multipart(
            data={
                "old_password": "1234",
                "password1": "NewSecurePass123!",
                "password2": "NewSecurePass123!",
            },
            boundary=BOUNDARY,
        ),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    no_perms_staff_client.user.user_permissions.add(change_perm)
    resp = no_perms_staff_client.post(
        "/api/password_change/",
        data=encode_multipart(
            data={
                "old_password": "1234",
                "password1": "NewSecurePass123!",
                "password2": "NewSecurePass123!",
            },
            boundary=BOUNDARY,
        ),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_200_OK

    # Verify password was changed
    user.refresh_from_db()
    assert user.password != old_password_hash
    assert user.check_password("NewSecurePass123!")


def test_password_change_multiple_times(db, staff_client):
    resp = staff_client.post(
        "/api/password_change/",
        data=encode_multipart(
            data={
                "old_password": "1234",
                "password1": "NewSecurePass123!",
                "password2": "NewSecurePass123!",
            },
            boundary=BOUNDARY,
        ),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_200_OK
    assert staff_client.user.check_password("NewSecurePass123!")

    resp = staff_client.post(
        "/api/password_change/",
        data=encode_multipart(
            data={
                "old_password": "NewSecurePass123!",
                "password1": "NewSecurePass123123!",
                "password2": "NewSecurePass123123!",
            },
            boundary=BOUNDARY,
        ),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_200_OK
    staff_client.user.refresh_from_db()
    assert staff_client.user.check_password("NewSecurePass123123!")


def test_password_change_preserves_user_data(db, staff_client):
    user = staff_client.user
    original_username = user.username
    original_email = user.email
    original_first_name = user.first_name
    original_last_name = user.last_name
    original_is_active = user.is_active
    original_is_staff = user.is_staff

    resp = staff_client.post(
        "/api/password_change/",
        data=encode_multipart(
            data={
                "old_password": "1234",
                "password1": "NewSecurePass123!",
                "password2": "NewSecurePass123!",
            },
            boundary=BOUNDARY,
        ),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.status_code == status.HTTP_200_OK

    # Verify other user data remains unchanged
    user.refresh_from_db()
    assert user.username == original_username
    assert user.email == original_email
    assert user.first_name == original_first_name
    assert user.last_name == original_last_name
    assert user.is_active == original_is_active
    assert user.is_staff == original_is_staff
