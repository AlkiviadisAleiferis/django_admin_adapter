import pytest

from django.contrib import admin
from rest_framework.test import APIClient
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_admin_adapter import AdminAPIAdapter, AdminSiteBasePermission


adapter = AdminAPIAdapter(admin.site)
NON_AUTH_URLS = [
    url
    for url in adapter.get_urls()
    if url.name not in AdminAPIAdapter.authentication_views_names
]


@pytest.mark.parametrize("url", NON_AUTH_URLS)
def test_admin_views_default_authentication_and_permission_classes(url):
    assert url.callback.cls.authentication_classes == [JWTAuthentication]
    assert url.callback.cls.permission_classes == [AdminSiteBasePermission]


# No Authentication Response


@pytest.mark.parametrize("url", NON_AUTH_URLS)
def test_admin_api_unauthenticated_access_returns_401(url):
    api_client = APIClient()
    response = api_client.get("/api/" + url.pattern._route)
    assert response.status_code == 401


# No Base Permission Response
# `AdminSite.has_base_permission` must be called
# and return False if `user.is_staff` is False


@pytest.mark.parametrize("url", NON_AUTH_URLS)
def test_admin_api_no_site_base_permission_returns_403(non_staff_client, url, mocker):
    spy = mocker.spy(admin.site, "has_permission")
    response = non_staff_client.get("/api/" + url.pattern._route)
    assert response.status_code == 403
    spy.assert_called_once()
