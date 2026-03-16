from django.contrib.admin import site
from backend.real_estate import models as real_estate_models
from backend.common import models as common_models
from backend.organization import models as organization_models
from django.contrib.auth import models as auth_models


class DummyRequest:
    def __init__(self, user):
        self.user = user


def get_sidebar_registry(user):
    request = DummyRequest(user)

    permissions_admin = site._registry[auth_models.Permission]
    groups_admin = site._registry[auth_models.Group]
    users_admin = site._registry[organization_models.User]
    projects_admin = site._registry[real_estate_models.Project]
    properties_admin = site._registry[real_estate_models.Property]
    agreements_admin = site._registry[real_estate_models.Agreement]
    contacts_admin = site._registry[common_models.Contact]
    emails_admin = site._registry[common_models.Email]

    has_permission_perm = permissions_admin.has_module_permission(
        request
    ) and permissions_admin.has_view_or_change_permission(request, None)
    has_group_perm = groups_admin.has_module_permission(
        request
    ) and groups_admin.has_view_or_change_permission(request, None)
    has_user_perm = users_admin.has_module_permission(
        request
    ) and users_admin.has_view_or_change_permission(request, None)
    has_change_user_perm = users_admin.has_module_permission(
        request
    ) and users_admin.has_change_permission(request, None)
    has_project_perm = projects_admin.has_module_permission(
        request
    ) and projects_admin.has_view_or_change_permission(request, None)
    has_property_perm = properties_admin.has_module_permission(
        request
    ) and properties_admin.has_view_or_change_permission(request, None)
    has_agreement_perm = agreements_admin.has_module_permission(
        request
    ) and agreements_admin.has_view_or_change_permission(request, None)
    has_contact_perm = contacts_admin.has_module_permission(
        request
    ) and contacts_admin.has_view_or_change_permission(request, None)
    has_email_perm = emails_admin.has_module_permission(
        request
    ) and emails_admin.has_view_or_change_permission(request, None)

    common_entries = {
        "type": "dropdown",
        "label": "Common",
        "icon": None,
        "dropdown_entries": [
            *(
                [
                    {
                        "type": "model",
                        "label": "Contacts",
                        "icon": "fa-regular fa-address-book",
                        "app_name": "common",
                        "model_name": "contact",
                        "permissions": {
                            "view": contacts_admin.has_view_permission(request, None),
                            "add": contacts_admin.has_add_permission(request),
                            "delete": contacts_admin.has_delete_permission(request, None),
                        },
                    }
                ]
                if has_contact_perm
                else []
            ),
            *(
                [
                    {
                        "type": "model",
                        "label": "Emails",
                        "icon": "fa-solid fa-email",
                        "app_name": "common",
                        "model_name": "email",
                        "permissions": {
                            "view": emails_admin.has_view_permission(request, None),
                            "add": emails_admin.has_add_permission(request),
                            "delete": emails_admin.has_delete_permission(request, None),
                        },
                    }
                ]
                if has_email_perm
                else []
            ),
        ],
    }
    if not common_entries["dropdown_entries"]:
        common_entries = []
    else:
        common_entries = [common_entries]

    return {
        "sidebar": [
            {
                "type": "view",
                "label": "Dummy View",
                "client_view_path": "client_dummy_view_path/",
                "icon": "fa-regular fa-house",
                "view_name": "dummy_view",
            },
            *(
                [
                    {
                        "type": "model",
                        "label": "Permissions",
                        "icon": None,
                        "app_name": "auth",
                        "model_name": "permission",
                        "permissions": {
                            "view": permissions_admin.has_view_permission(request, None),
                            "add": permissions_admin.has_add_permission(request),
                            "delete": permissions_admin.has_delete_permission(
                                request, None
                            ),
                        },
                    }
                ]
                if has_permission_perm
                else []
            ),
            *(
                [
                    {
                        "type": "model",
                        "label": "Groups",
                        "icon": None,
                        "app_name": "auth",
                        "model_name": "group",
                        "permissions": {
                            "view": groups_admin.has_view_permission(request, None),
                            "add": groups_admin.has_add_permission(request),
                            "delete": groups_admin.has_delete_permission(request, None),
                        },
                    }
                ]
                if has_group_perm
                else []
            ),
            *(
                [
                    {
                        "type": "model",
                        "label": "Users",
                        "icon": None,
                        "app_name": "organization",
                        "model_name": "user",
                        "permissions": {
                            "view": users_admin.has_view_permission(request, None),
                            "add": users_admin.has_add_permission(request),
                            "delete": users_admin.has_delete_permission(request, None),
                        },
                    }
                ]
                if has_user_perm
                else []
            ),
            {
                "type": "dropdown",
                "label": "Real Estate",
                "icon": None,
                "dropdown_entries": [
                    *(
                        [
                            {
                                "type": "model",
                                "label": "Projects",
                                "icon": "fa-regular fa-house",
                                "app_name": "real_estate",
                                "model_name": "project",
                                "permissions": {
                                    "view": projects_admin.has_view_permission(
                                        request, None
                                    ),
                                    "add": projects_admin.has_add_permission(request),
                                    "delete": projects_admin.has_delete_permission(
                                        request, None
                                    ),
                                },
                            }
                        ]
                        if has_project_perm
                        else []
                    ),
                    *(
                        [
                            {
                                "type": "model",
                                "label": "Properties",
                                "icon": "fa-regular fa-house",
                                "app_name": "real_estate",
                                "model_name": "property",
                                "permissions": {
                                    "view": properties_admin.has_view_permission(
                                        request, None
                                    ),
                                    "add": properties_admin.has_add_permission(request),
                                    "delete": properties_admin.has_delete_permission(
                                        request, None
                                    ),
                                },
                            }
                        ]
                        if has_property_perm
                        else []
                    ),
                    *(
                        [
                            {
                                "type": "model",
                                "label": "Agreements",
                                "icon": None,
                                "app_name": "real_estate",
                                "model_name": "agreement",
                                "permissions": {
                                    "view": agreements_admin.has_view_permission(
                                        request, None
                                    ),
                                    "add": agreements_admin.has_add_permission(request),
                                    "delete": agreements_admin.has_delete_permission(
                                        request, None
                                    ),
                                },
                            }
                        ]
                        if has_agreement_perm
                        else []
                    ),
                    {
                        "type": "view",
                        "label": "Dummy View",
                        "client_view_path": "client_dummy_view_path/",
                        "icon": "fa-regular fa-house",
                        "view_name": "dummy_view",
                    },
                ],
            },
            *common_entries,
        ],
        "profile": {
            "user_pk": user.pk if has_user_perm else None,
            "app_name": "organization" if has_user_perm else None,
            "model_name": "user" if has_user_perm else None,
            "password_change": has_change_user_perm,
        },
        "extra": None,
    }
