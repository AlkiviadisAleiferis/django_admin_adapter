import pytest
from django.contrib.admin import site
from django_admin_adapter.views.base import BaseAdminObjectAPIView
from django_admin_adapter.views.object import BaseObjectUIAPIView
from django_admin_adapter.exceptions import InvalidURLParamsError
from django_admin_adapter.viewmap import VIEWMAP

from admin_api.model_admins import EmailAdmin
from backend.common.models import Email
from backend.tests import factories

BASE_ADMIN_OBJECT_EXTENDERS = [
    VIEWMAP["admin_object_edit"][1],
    VIEWMAP["admin_object_delete_confirm"][1],
    VIEWMAP["admin_object_history"][1],
    VIEWMAP["admin_object_view"][1],
    VIEWMAP["admin_object"][1],
]


def test_BaseAdminObjectAPIView_inheritance():
    assert BASE_ADMIN_OBJECT_EXTENDERS[0].__mro__[1] == BaseObjectUIAPIView
    assert BASE_ADMIN_OBJECT_EXTENDERS[0].__mro__[2] == BaseAdminObjectAPIView
    #
    for viewclass in BASE_ADMIN_OBJECT_EXTENDERS[1:]:
        assert issubclass(viewclass, BaseAdminObjectAPIView)


@pytest.mark.parametrize("viewclass", BASE_ADMIN_OBJECT_EXTENDERS)
def test_BaseAdminObjectAPIView_pk_missing(viewclass, api_rf, staff_client):
    request = api_rf.get("/", content_type="application/json", format="json")
    request.query_params = {}
    request.user = staff_client.user

    view = viewclass()
    view.request = request
    view._admin_site = site
    view.kwargs = {"app_name": "common", "model_name": "email"}

    with pytest.raises(
        InvalidURLParamsError,
        match="Missing URL params \(2\)",
    ):
        view.initial(request)


@pytest.mark.parametrize("viewclass", BASE_ADMIN_OBJECT_EXTENDERS)
def test_BaseAdminObjectAPIView_all_ok(viewclass, api_rf, staff_client):
    request = api_rf.get("/", content_type="application/json", format="json")
    request.query_params = {}
    request.user = staff_client.user

    email_obj = factories.EmailFactory()
    view = viewclass()
    view._admin_site = site
    view.request = request
    view.kwargs = {"app_name": "common", "model_name": "email", "pk": f"{email_obj.pk}"}

    result = view.initial(request)

    assert result is None
    assert view.model == Email
    assert isinstance(view.model_admin, EmailAdmin)
    assert isinstance(view.obj, Email)
    assert view.obj == email_obj
