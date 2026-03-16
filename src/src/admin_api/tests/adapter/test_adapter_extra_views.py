import pytest
from django.contrib.admin import site as default_admin_site
from rest_framework.views import APIView
from rest_framework.throttling import BaseThrottle
from django_admin_adapter.adapter import (
    AdminAPIAdapter,
    AdminAPIAdapterError,
    AdminAnonRateThrottle,
    AdminUserRateThrottle,
)
from django_admin_adapter.viewmap import VIEWMAP


class DummyView(APIView):
    pass


class DummyAnonThrottle(BaseThrottle):
    pass


class DummyUserThrottle(BaseThrottle):
    pass


def test_default_views():
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        extra_views={},
    )
    assert adapter.views_mapping == VIEWMAP


# --- Success Cases ---


def test_valid_extra_views_with_throttles():
    extra_views = {
        "dummy_view": (
            "dummy/path/",
            DummyView,
            [DummyAnonThrottle, DummyUserThrottle],
        )
    }
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        extra_views=extra_views,
    )

    assert "dummy_view" in adapter.views_mapping
    assert adapter.views_mapping["dummy_view"][0] == "dummy/path/"
    assert adapter.views_mapping["dummy_view"][1] == DummyView
    assert adapter.views_mapping["dummy_view"][2] == [
        DummyAnonThrottle,
        DummyUserThrottle,
    ]


def test_valid_extra_views_with_none_throttles():
    extra_views = {
        "dummy_view": (
            "dummy/path/",
            DummyView,
            None,
        )
    }
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        extra_views=extra_views,
    )

    assert "dummy_view" in adapter.views_mapping
    assert adapter.views_mapping["dummy_view"][0] == "dummy/path/"
    assert adapter.views_mapping["dummy_view"][1] == DummyView
    assert adapter.views_mapping["dummy_view"][2] is None


def test_empty_extra_views():
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        extra_views={},
    )
    assert adapter.views_mapping == VIEWMAP

    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        extra_views=None,
    )
    assert adapter.views_mapping == VIEWMAP


# --- Error Cases ---


@pytest.mark.parametrize("extra_views", [[1, 2], 4, 4.5, "str"])
def test_extra_views_not_dict(extra_views):
    with pytest.raises(AdminAPIAdapterError, match="extra_views must be of type dict"):
        AdminAPIAdapter(admin_site=default_admin_site, extra_views=extra_views)


def test_extra_views_tuple_wrong_length():
    extra_views = {
        "dummy_view": ("dummy/path/", DummyView)  # Only 2 elements
    }
    with pytest.raises(AdminAPIAdapterError, match="must be in"):
        AdminAPIAdapter(admin_site=default_admin_site, extra_views=extra_views)
    extra_views = {
        "dummy_view": ("dummy/path/", DummyView, None, None)  # Only 2 elements
    }
    with pytest.raises(AdminAPIAdapterError, match="must be in"):
        AdminAPIAdapter(admin_site=default_admin_site, extra_views=extra_views)


def test_extra_views_path_not_str():
    extra_views = {"dummy_view": (123, DummyView, [DummyAnonThrottle, DummyUserThrottle])}
    with pytest.raises(
        AdminAPIAdapterError, match="view path for 'dummy_view' must be of type str"
    ):
        AdminAPIAdapter(admin_site=default_admin_site, extra_views=extra_views)


def test_extra_views_view_not_apiview():
    class NotAView:
        pass

    extra_views = {
        "dummy_view": ("dummy/path/", NotAView, [DummyAnonThrottle, DummyUserThrottle])
    }
    with pytest.raises(
        AdminAPIAdapterError, match="must be a subclass of rest_framework.views.APIView"
    ):
        AdminAPIAdapter(admin_site=default_admin_site, extra_views=extra_views)


def test_extra_views_throttles_not_list_or_tuple():
    extra_views = {"dummy_view": ("dummy/path/", DummyView, "notalist")}
    with pytest.raises(AdminAPIAdapterError, match="must be of type list or tuple"):
        AdminAPIAdapter(admin_site=default_admin_site, extra_views=extra_views)


def test_extra_views_throttles_wrong_length():
    extra_views = {"dummy_view": ("dummy/path/", DummyView, [DummyAnonThrottle])}
    with pytest.raises(AdminAPIAdapterError, match="must be of length 2"):
        AdminAPIAdapter(admin_site=default_admin_site, extra_views=extra_views)


def test_extra_views_throttle_not_subclass():
    class NotAThrottle:
        pass

    extra_views = {
        "dummy_view": ("dummy/path/", DummyView, [NotAThrottle, DummyUserThrottle])
    }
    with pytest.raises(
        AdminAPIAdapterError,
        match="must be a subclass of rest_framework.throttling.BaseThrottle",
    ):
        AdminAPIAdapter(admin_site=default_admin_site, extra_views=extra_views)
