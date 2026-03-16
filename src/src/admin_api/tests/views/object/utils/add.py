from django.contrib.admin import site
from backend.real_estate import models as real_estate_models
from backend.common import models as common_models
from backend.organization import models as organization_models
from .common import DummyRequest


def get_object_add_data(user):
    """
    Get the object add data.
    Replicates what the view should return.

    ARGS:
        user: The user to generate view data for

    RETURNS:
        Dictionary containing the object add data
    """
    request = DummyRequest(user)

    users_admin = site._registry[organization_models.User]
    projects_admin = site._registry[real_estate_models.Project]
    properties_admin = site._registry[real_estate_models.Property]
    agreements_admin = site._registry[real_estate_models.Agreement]
    contacts_admin = site._registry[common_models.Contact]

    inline_add_perm = user.has_perm("real_estate.add_agreementcommission")
    inline_change_perm = user.has_perm("real_estate.change_agreementcommission")
    inline_delete_perm = user.has_perm("real_estate.delete_agreementcommission")
    inline_view_perm = (
        user.has_perm("real_estate.view_agreementcommission") or inline_change_perm
    )

    DELETE_field = (
        {
            "DELETE": {
                "type": "BooleanField",
                "label": "Delete",
                "required": False,
                "help_text": "",
                "initial": None,
            }
        }
        if inline_delete_perm
        else {}
    )

    inline_management_form = {
        "fields": {
            "TOTAL_FORMS": {
                "type": "IntegerField",
                "label": None,
                "required": True,
                "help_text": "",
                "initial": 1 if inline_add_perm else 0,
            },
            "INITIAL_FORMS": {
                "type": "IntegerField",
                "label": None,
                "required": True,
                "help_text": "",
                "initial": 0,
            },
            "MIN_NUM_FORMS": {
                "type": "IntegerField",
                "label": None,
                "required": False,
                "help_text": "",
                "initial": 0,
            },
            "MAX_NUM_FORMS": {
                "type": "IntegerField",
                "label": None,
                "required": False,
                "help_text": "",
                "initial": 1000 if inline_add_perm else 0,
            },
        },
        "readonly_fields": {},
        "prefix": "commissions",
    }

    inline_extra_form = {
        "readonly_fields": {
            "created_at": {
                "type": "DateTimeField",
                "value": None,
                "help_text": "",
            },
            "updated_at": {
                "type": "DateTimeField",
                "value": None,
                "help_text": "",
            },
        },
        "fields": {
            "agreement": {
                "type": "InlineForeignKeyField",
                "label": "Agreement",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "beneficiary": {
                "type": "ModelChoiceField",
                "label": "Beneficiary",
                "required": True,
                "help_text": "",
                "initial": None,
                "model": "contact",
                "app": "common",
                "permissions": {
                    "view": contacts_admin.has_view_permission(request, None),
                    "add": contacts_admin.has_add_permission(request),
                    "change": contacts_admin.has_change_permission(request, None),
                    "delete": contacts_admin.has_delete_permission(request, None),
                },
                "autocomplete": True,
            },
            "value": {
                "type": "DecimalField",
                "label": "Value",
                "required": True,
                "help_text": "",
                "initial": None,
            },
            "id": {
                "type": "hidden",
                "label": "pk",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            # only append if user has delete permission
            **DELETE_field,
        },
        "prefix": "commissions-__prefix__",
    }
    if inline_add_perm:
        inline_forms = [
            {
                "readonly_fields": {
                    "created_at": {
                        "type": "DateTimeField",
                        "value": None,
                        "help_text": "",
                    },
                    "updated_at": {
                        "type": "DateTimeField",
                        "value": None,
                        "help_text": "",
                    },
                },
                "fields": {
                    "agreement": {
                        "type": "InlineForeignKeyField",
                        "label": "Agreement",
                        "required": False,
                        "help_text": "",
                        "initial": None,
                    },
                    "beneficiary": {
                        "type": "ModelChoiceField",
                        "label": "Beneficiary",
                        "required": True,
                        "help_text": "",
                        "initial": None,
                        "model": "contact",
                        "app": "common",
                        "permissions": {
                            "view": contacts_admin.has_view_permission(request, None),
                            "add": contacts_admin.has_add_permission(request),
                            "change": contacts_admin.has_change_permission(request, None),
                            "delete": contacts_admin.has_delete_permission(request, None),
                        },
                        "autocomplete": True,
                    },
                    "value": {
                        "type": "DecimalField",
                        "label": "Value",
                        "required": True,
                        "help_text": "",
                        "initial": None,
                    },
                    "id": {
                        "type": "hidden",
                        "label": "pk",
                        "required": False,
                        "help_text": "",
                        "initial": None,
                    },
                    # only append if user has delete permission
                    **DELETE_field,
                },
                "prefix": "commissions-0",
            }
        ]
    else:
        inline_forms = []

    return {
        # ---------------------------------------------
        # object
        "object_repr": None,
        "model": "agreement",
        "app": "real_estate",
        # ---------------------------------------------
        # UI
        "fieldsets": [
            (
                None,
                {
                    "fields": (
                        "created_at",
                        "updated_at",
                        "type",
                        "status",
                        "agreement_signing_date",
                        "signing_time",
                        "assigned_to",
                        "project",
                        "property",
                        "unique_id",
                        "website_url",
                        "slug",
                        "closure_percentage",
                        "agreement_int",
                        "description",
                        "valid_from",
                        "valid_until",
                        "cancel_date",
                        "reservation_date",
                        "price",
                        "down_payment",
                        "private_agreement_date",
                    )
                },
            )
        ],
        # ---------------------------------------------
        # form
        "readonly_fields": {
            "created_at": {
                "type": "DateTimeField",
                "value": None,
                "help_text": "",
            },
            "updated_at": {
                "type": "DateTimeField",
                "value": None,
                "help_text": "",
            },
        },
        "fields": {
            "type": {
                "type": "TypedChoiceField",
                "label": "Type",
                "required": True,
                "help_text": "type after creation gets locked",
                "initial": None,
                "choices": [
                    ("", "---------"),
                    ("COS", "Contract of Sale"),
                    ("TEN", "Tenancy Agreement"),
                    ("PMG", "Property management Agreement"),
                ],
            },
            "status": {
                "type": "TypedChoiceField",
                "label": "Status",
                "required": True,
                "help_text": "After setting to Agreed or Cancelled, <br>the Agreement gets locked and cannot be edited",
                "initial": None,
                "choices": [
                    ("", "---------"),
                    ("OPN", "Open"),
                    ("RSV", "Reserved"),
                    ("CNL", "Cancelled"),
                    ("AGR", "Agreed"),
                ],
            },
            "agreement_signing_date": {
                "type": "DateField",
                "label": "Agreement signing date",
                "required": False,
                "help_text": "If a date is provided, the agreement will be thought as accepted. <br>This will lock the agreement for edit.",
                "initial": None,
            },
            "signing_time": {
                "type": "TimeField",
                "label": "Signing time",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "assigned_to": {
                "type": "ModelChoiceField",
                "label": "Assigned to",
                "required": False,
                "help_text": "",
                "initial": None,
                "model": "user",
                "app": "organization",
                "permissions": {
                    "view": users_admin.has_view_permission(request, None),
                    "add": users_admin.has_add_permission(request),
                    "change": users_admin.has_change_permission(request, None),
                    "delete": users_admin.has_delete_permission(request, None),
                },
                "autocomplete": True,
            },
            "project": {
                "type": "ModelChoiceField",
                "label": "Project",
                "required": False,
                "help_text": "",
                "initial": None,
                "model": "project",
                "app": "real_estate",
                "permissions": {
                    "view": projects_admin.has_view_permission(request, None),
                    "add": projects_admin.has_add_permission(request),
                    "change": projects_admin.has_change_permission(request, None),
                    "delete": projects_admin.has_delete_permission(request, None),
                },
                "autocomplete": True,
            },
            "property": {
                "type": "ModelChoiceField",
                "label": "Property",
                "required": False,
                "help_text": "",
                "initial": None,
                "model": "property",
                "app": "real_estate",
                "permissions": {
                    "view": properties_admin.has_view_permission(request, None),
                    "add": properties_admin.has_add_permission(request),
                    "change": properties_admin.has_change_permission(request, None),
                    "delete": properties_admin.has_delete_permission(request, None),
                },
                "autocomplete": True,
            },
            "unique_id": {
                "type": "UUIDField",
                "label": "Unique id",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "website_url": {
                "type": "URLField",
                "label": "Website url",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "slug": {
                "type": "SlugField",
                "label": "Slug",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "closure_percentage": {
                "type": "FloatField",
                "label": "Closure percentage",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "agreement_int": {
                "type": "IntegerField",
                "label": "Agreement int",
                "required": False,
                "help_text": "needed an integer field",
                "initial": 1,
            },
            "description": {
                "type": "TextField",
                "label": "Description",
                "required": False,
                "help_text": "",
                "initial": "",
                "rows": "10",
                "cols": "40",
            },
            "valid_from": {
                "type": "DateField",
                "label": "Valid from",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "valid_until": {
                "type": "DateField",
                "label": "Valid until",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "cancel_date": {
                "type": "DateField",
                "label": "Cancel date",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "reservation_date": {
                "type": "DateField",
                "label": "Reservation date",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "price": {
                "type": "DecimalField",
                "label": "Price",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "down_payment": {
                "type": "DecimalField",
                "label": "Down payment",
                "required": False,
                "help_text": "",
                "initial": None,
            },
            "private_agreement_date": {
                "type": "DateField",
                "label": "Private agreement date",
                "required": False,
                "help_text": "",
                "initial": None,
            },
        },
        "prefix": None,
        # ---------------------------------------------
        # inlines
        "inlines": [
            {
                "type": "tabular",
                "label": "Commissions",
                "model": "agreementcommission",
                "app": "real_estate",
                "permissions": {
                    "view": inline_view_perm,
                    "add": inline_add_perm,
                    "change": inline_change_perm,
                    "delete": inline_delete_perm,
                },
                "pk_name": "id",
                "prefix": "commissions",
                "management_form": inline_management_form,
                "forms": inline_forms,
                "extra_form": inline_extra_form,
                "min_forms_num": 0,
                "max_forms_num": 1000 if inline_add_perm else 0,
            }
        ],
        # ---------------------------------------------
        # extra_data
        "extra_data": agreements_admin.get_add_extra_data(request),
    }
