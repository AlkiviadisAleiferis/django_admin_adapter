from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from .views import DummyExtraView
from django_admin_adapter.adapter import AdminAPIAdapter


admin_adapter = AdminAPIAdapter(
    admin.site,
    extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
    sidebar_registry=[
        {
            "type": "view",
            "label": "Dummy View",
            "client_view_path": "client_dummy_view_path/",
            "icon": "fa-regular fa-house",
            "view_name": "dummy_view",
        },
        {
            "type": "model",
            "label": "Permissions",
            "app_name": "auth",
            "model_name": "permission",
        },
        {
            "type": "model",
            "label": "Groups",
            "app_name": "auth",
            "model_name": "group",
        },
        {
            "type": "model",
            "label": "Users",
            "app_name": "organization",
            "model_name": "user",
        },
        {
            "type": "dropdown",
            "label": "Real Estate",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Projects",
                    "icon": "fa-regular fa-house",
                    "app_name": "real_estate",
                    "model_name": "project",
                },
                {
                    "type": "model",
                    "label": "Properties",
                    "icon": "fa-regular fa-house",
                    "app_name": "real_estate",
                    "model_name": "property",
                },
                {
                    "type": "model",
                    "label": "Agreements",
                    "app_name": "real_estate",
                    "model_name": "agreement",
                },
                {
                    "type": "view",
                    "label": "Dummy View",
                    "client_view_path": "client_dummy_view_path/",
                    "icon": "fa-regular fa-house",
                    "view_name": "dummy_view",
                },
            ],
        },
        {
            "type": "dropdown",
            "label": "Common",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Contacts",
                    "icon": "fa-regular fa-address-book",
                    "app_name": "common",
                    "model_name": "contact",
                },
                {
                    "type": "model",
                    "label": "Emails",
                    "icon": "fa-solid fa-email",
                    "app_name": "common",
                    "model_name": "email",
                },
            ],
        },
    ],
)


urlpatterns = [
    path("api/", include(admin_adapter.get_urls())),
]

if settings.DEBUG:
    urlpatterns.insert(0, path("profiling/", include("silk.urls", namespace="silk")))
