import pytest
from django_admin_adapter.adapter import (
    AdminAPIAdapter,
    AdminAPIAdapterError,
    AdminAnonRateThrottle,
    AdminUserRateThrottle,
)
from rest_framework.throttling import BaseThrottle
from django.contrib.admin import site as default_admin_site


class DummyAnonThrottle(BaseThrottle): ...


class DummyUserThrottle(BaseThrottle): ...


class DummyAuthThrottle(BaseThrottle): ...


class NotAThrottle: ...


def test_custom_throttle_classes_are_set():
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        default_anon_throttle_class=DummyAnonThrottle,
        default_user_throttle_class=DummyUserThrottle,
        authentication_throttle_class=DummyAuthThrottle,
    )
    assert adapter.default_anon_throttle_class == DummyAnonThrottle
    assert adapter.default_user_throttle_class == DummyUserThrottle
    assert adapter.authentication_throttle_class == DummyAuthThrottle


def test_only_custom_anon_throttle_class():
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        default_anon_throttle_class=DummyAnonThrottle,
        authentication_throttle_class=DummyAuthThrottle,
    )
    assert adapter.default_anon_throttle_class == DummyAnonThrottle
    assert adapter.default_user_throttle_class == AdminUserRateThrottle
    assert adapter.authentication_throttle_class == DummyAuthThrottle


def test_only_custom_user_throttle_class():
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        default_user_throttle_class=DummyUserThrottle,
        authentication_throttle_class=DummyAuthThrottle,
    )
    assert adapter.default_anon_throttle_class == AdminAnonRateThrottle
    assert adapter.default_user_throttle_class == DummyUserThrottle
    assert adapter.authentication_throttle_class == DummyAuthThrottle


def test_only_custom_authentication_throttle_class():
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        authentication_throttle_class=DummyAuthThrottle,
    )
    assert adapter.default_anon_throttle_class == AdminAnonRateThrottle
    assert adapter.default_user_throttle_class == AdminUserRateThrottle
    assert adapter.authentication_throttle_class == DummyAuthThrottle


def test_auth_views_authentication_throttle_class():
    # default throttle for auth (none)
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
    )
    for view_name in adapter.views_mapping:
        if view_name not in adapter.authentication_views_names:
            continue
        path = adapter.build_view_path(view_name)
        view_class = path.callback.cls

        assert view_class.throttle_classes == []

    # with custom auth throttle
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        authentication_throttle_class=DummyAuthThrottle,
    )
    for view_name in adapter.views_mapping:
        if view_name not in adapter.authentication_views_names:
            continue
        path = adapter.build_view_path(view_name)
        view_class = path.callback.cls

        assert view_class.throttle_classes == [
            DummyAuthThrottle,
        ]


# --- Error Cases ---


@pytest.mark.parametrize("throttle_class", [123, "notaclass", DummyAnonThrottle()])
def test_default_anon_throttle_class_not_a_class(throttle_class):
    with pytest.raises(
        AdminAPIAdapterError,
        match="`default_anon_throttle_class` provided is not a class",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            default_anon_throttle_class=throttle_class,
        )


def test_default_anon_throttle_class_not_a_subclass():
    with pytest.raises(
        AdminAPIAdapterError,
        match="`default_anon_throttle_class` provided is not of type `BaseThrottle`",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            default_anon_throttle_class=NotAThrottle,
        )


@pytest.mark.parametrize("throttle_class", [123, "notaclass", DummyUserThrottle()])
def test_default_user_throttle_class_not_a_class(throttle_class):
    with pytest.raises(
        AdminAPIAdapterError,
        match="`default_user_throttle_class` provided is not a class",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            default_user_throttle_class=throttle_class,
        )


def test_default_user_throttle_class_not_a_subclass():
    with pytest.raises(
        AdminAPIAdapterError,
        match="`default_user_throttle_class` provided is not of type `BaseThrottle`",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            default_user_throttle_class=NotAThrottle,
        )


@pytest.mark.parametrize("throttle_class", [123, "notaclass", DummyAnonThrottle()])
def test_authentication_throttle_class_not_a_class(throttle_class):
    with pytest.raises(
        AdminAPIAdapterError,
        match="`authentication_throttle_class` provided is not a class",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            authentication_throttle_class=throttle_class,
        )


def test_authentication_throttle_class_not_a_subclass():
    with pytest.raises(
        AdminAPIAdapterError,
        match="`authentication_throttle_class` provided is not of type `BaseThrottle`",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            authentication_throttle_class=NotAThrottle,
        )
