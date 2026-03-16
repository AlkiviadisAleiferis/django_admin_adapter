import pytest
from django.contrib.admin.sites import AdminSite, site
from django.urls import path
from django_admin_adapter.adapter import (
    AdminAPIAdapter,
    VIEWMAP,
    AdminAnonRateThrottle,
    AdminUserRateThrottle,
)
from django_admin_adapter.serializers import (
    AdminHistorySerializer,
    AdminListSerializer,
    AdminObjectViewSerializer,
)
from rest_framework_simplejwt.authentication import JWTAuthentication


# pass the default admin site of the admin_api project
@pytest.fixture
def adapter():
    # Minimum arguments: only admin_site
    return AdminAPIAdapter(admin_site=site)


def test_admin_site_is_set(adapter):
    assert isinstance(adapter.admin_site, AdminSite)


def test_default_views_mapping_is_deepcopy_of_viewmap(adapter):
    # Should be a deepcopy, not the same object
    assert adapter.views_mapping is not VIEWMAP
    assert adapter.views_mapping == VIEWMAP


def test_default_authentication_views_names(adapter):
    assert adapter.authentication_views_names == ("token_obtain_pair", "token_refresh")


def test_default_urls(adapter):
    urlpatterns = adapter.get_urls()
    expected_urls = []

    for view_name in adapter.views_mapping:
        view_url, ViewClass, throttle_classes_list = adapter.views_mapping[view_name]

        if throttle_classes_list is None:
            throttle_classes_list = [
                adapter.default_anon_throttle_class,
                adapter.default_user_throttle_class,
            ]

        # subclassing avoids name classing
        class AdminAdapterAPIView(ViewClass):
            __name__ = ViewClass.__name__
            throttle_classes = throttle_classes_list
            _admin_site = adapter.admin_site
            _adapter_instance = adapter
            _admin_view_name = view_name

        # add default authentication and permission classes
        # to every non-authentication view
        if view_name not in adapter.authentication_views_names:
            AdminAdapterAPIView.authentication_classes = [adapter.authentication_class]
            AdminAdapterAPIView.permission_classes = [adapter.base_permission_class]

        expected_urls.append(
            path(view_url, AdminAdapterAPIView.as_view(), name=view_name)
        )

    for i, view_path in enumerate(urlpatterns):
        assert str(view_path.pattern) == str(expected_urls[i].pattern)
        assert view_path.name == expected_urls[i].name
        assert view_path.default_args == expected_urls[i].default_args
        # inherited from the same view class
        assert (
            view_path.callback.cls.__mro__[1] == expected_urls[i].callback.cls.__mro__[1]
        )


def test_default_sidebar_registry(adapter):
    assert adapter.sidebar_registry == []


def test_default_throttle_classes(adapter):
    assert (
        adapter.default_anon_throttle_class is AdminAPIAdapter.default_anon_throttle_class
    )
    assert (
        adapter.default_user_throttle_class is AdminAPIAdapter.default_user_throttle_class
    )
    assert issubclass(adapter.default_anon_throttle_class, AdminAnonRateThrottle)
    assert issubclass(adapter.default_user_throttle_class, AdminUserRateThrottle)
    assert adapter.authentication_throttle_class is None


def test_default_history_page_size(adapter):
    assert adapter.history_page_size == 30


def test_default_authentication_class(adapter):
    assert adapter.authentication_class is JWTAuthentication


def test_default_view_path_builds(adapter):
    for view_name in VIEWMAP:
        path = adapter.build_view_path(view_name)
        assert path.name == view_name
        assert path.pattern._route == VIEWMAP[view_name][0]

        view_class = path.callback.cls

        if view_name not in adapter.authentication_views_names:
            assert view_class.throttle_classes == [
                AdminAnonRateThrottle,
                AdminUserRateThrottle,
            ]
        else:
            assert view_class.throttle_classes == []

        assert view_class._admin_site == adapter.admin_site
        assert view_class._adapter_instance == adapter
        assert view_class._admin_view_name == view_name
        # make sure they inherit from the same class
        assert VIEWMAP[view_name][1] == view_class.__mro__[1]
    assert set(VIEWMAP) == set(adapter.views_mapping)


def test_admin_default_serializer_classes(adapter):
    assert adapter.history_serializer_class is AdminHistorySerializer
    assert adapter.list_serializer_class is AdminListSerializer
    assert adapter.object_serializer_class is AdminObjectViewSerializer
