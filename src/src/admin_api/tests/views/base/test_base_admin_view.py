import pytest
from django.contrib.admin import site
from django_admin_adapter.views.base import BaseAdminAPIView
from django_admin_adapter.views.object import BaseObjectUIAPIView
from django_admin_adapter.exceptions import InvalidURLParamsError
from django_admin_adapter.viewmap import VIEWMAP

from admin_api.model_admins import EmailAdmin
from backend.common.models import Email

BASE_ADMIN_EXTENDERS = [
    VIEWMAP["admin_object_add"][1],
    VIEWMAP["admin_list_action_preview"][1],
    VIEWMAP["admin_list_action_execute"][1],
    VIEWMAP["admin_list_info"][1],
    VIEWMAP["admin_list_create"][1],
]


def test_BaseAdminAPIView_in_inheritance():
    assert BASE_ADMIN_EXTENDERS[0].__mro__[1] == BaseObjectUIAPIView
    assert BASE_ADMIN_EXTENDERS[0].__mro__[2] == BaseAdminAPIView
    #
    for viewclass in BASE_ADMIN_EXTENDERS[1:]:
        assert issubclass(viewclass, BaseAdminAPIView)


@pytest.mark.parametrize("viewclass", BASE_ADMIN_EXTENDERS)
def test_BaseAdminAPIView_app_name_or_model_name_kwargs_missing(
    viewclass, api_rf, staff_client
):
    request = api_rf.get("/", content_type="application/json", format="json")
    request.query_params = {}
    request.user = staff_client.user

    view = viewclass()
    view.request = request

    view.kwargs = {"model_name": "property"}
    with pytest.raises(
        InvalidURLParamsError,
        match="Missing URL params \(1\)\.",
    ):
        view.initial(request)

    view.kwargs = {"app_name": "real_estate"}
    with pytest.raises(
        InvalidURLParamsError,
        match="Missing URL params \(1\)\.",
    ):
        view.initial(request)


@pytest.mark.parametrize("viewclass", BASE_ADMIN_EXTENDERS)
def test_BaseAdminAPIView_non_existing_model(viewclass, api_rf, staff_client):
    request = api_rf.get("/", content_type="application/json", format="json")
    request.query_params = {}
    request.user = staff_client.user

    view = viewclass()
    view.request = request

    view.kwargs = {"app_name": "real_estate", "model_name": "non_existing_model"}
    with pytest.raises(
        InvalidURLParamsError,
        match="Invalid URL params \(1\)\.",
    ):
        view.initial(request)


@pytest.mark.parametrize("viewclass", BASE_ADMIN_EXTENDERS)
def test_BaseAdminAPIView_non_existing_model_admin(viewclass, api_rf, staff_client):
    request = api_rf.get("/", content_type="application/json", format="json")
    request.query_params = {}
    request.user = staff_client.user

    view = viewclass()
    view._admin_site = site
    view.request = request

    view.kwargs = {"app_name": "common", "model_name": "city"}
    with pytest.raises(
        InvalidURLParamsError,
        match="Invalid URL params \(2\)\.",
    ):
        view.initial(request)


@pytest.mark.parametrize("viewclass", BASE_ADMIN_EXTENDERS)
def test_BaseAdminAPIView_all_ok(viewclass, api_rf, staff_client):
    request = api_rf.get("/", content_type="application/json", format="json")
    request.query_params = {}
    request.user = staff_client.user

    view = viewclass()
    view._admin_site = site
    view.request = request

    view.kwargs = {"app_name": "common", "model_name": "email"}
    model_admin = view.initial(request)

    assert isinstance(model_admin, EmailAdmin)
    assert isinstance(view.model_admin, EmailAdmin)
    assert view.model == Email
