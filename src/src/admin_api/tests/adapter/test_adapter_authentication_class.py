import pytest
from django.contrib.admin import site as default_admin_site
from django_admin_adapter.adapter import (
    AdminAPIAdapter,
    AdminAPIAdapterError,
)
from rest_framework import authentication
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomAuthClass(authentication.BaseAuthentication): ...


class NotAuthClass: ...


def test_authentication_class_class_ok():
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        authentication_class=CustomAuthClass,
    )
    assert adapter.authentication_class == CustomAuthClass


# --- Error Cases ---


@pytest.mark.parametrize("authentication_class", [123, "notaclass", {}])
def test_authentication_class_not_a_class(authentication_class):
    with pytest.raises(
        AdminAPIAdapterError, match="The `authentication_class` provided is not a class."
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            authentication_class=authentication_class,
        )


def test_authentication_class_wrong_inheritance():
    with pytest.raises(
        AdminAPIAdapterError,
        match=(
            "The `authentication_class` provided is not a subclass of "
            "`rest_framework.authentication.BaseAuthentication`."
        ),
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            authentication_class=NotAuthClass,
        )


def test_views_custom_authentication():
    # default auth class (JWT)

    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
    )

    for view_name in adapter.views_mapping:
        if view_name in adapter.authentication_views_names:
            continue
        path = adapter.build_view_path(view_name)
        view_class = path.callback.cls
        assert view_class.authentication_classes == [JWTAuthentication]

    # with custom auth class

    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        authentication_class=CustomAuthClass,
    )

    for view_name in adapter.views_mapping:
        if view_name in adapter.authentication_views_names:
            continue
        path = adapter.build_view_path(view_name)
        view_class = path.callback.cls
        assert view_class.authentication_classes == [
            CustomAuthClass,
        ]
