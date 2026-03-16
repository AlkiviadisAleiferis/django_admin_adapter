from copy import deepcopy
from django.contrib.admin import site
from backend.real_estate import models as real_estate_models
from backend.common import models as common_models
from backend.organization import models as organization_models
from .common import DummyRequest


def get_object_edit_data(user, agreement):
    """
    Get the object edit data for an agreement object.
    Replicates what the view should return.
    It is essential part of the testing process.

    ARGS:
        user: The user to generate view data for
        agreement: The agreement instance to generate edit data for

    RETURNS:
        Dictionary containing the object edit data
    """
    request = DummyRequest(user)

    users_admin = site._registry[organization_models.User]
    projects_admin = site._registry[real_estate_models.Project]
    properties_admin = site._registry[real_estate_models.Property]
    agreements_admin = site._registry[real_estate_models.Agreement]
    contacts_admin = site._registry[common_models.Contact]

    # Get existing commissions
    commissions = agreement.commissions.all()

    inline_add_perm = user.has_perm("real_estate.add_agreementcommission")
    inline_change_perm = user.has_perm("real_estate.change_agreementcommission")
    inline_delete_perm = user.has_perm("real_estate.delete_agreementcommission")
    inline_view_perm = (
        user.has_perm("real_estate.view_agreementcommission") or inline_change_perm
    )
    any_view_perm = inline_view_perm or inline_change_perm

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
        #
        if inline_delete_perm
        else {}
    )

    commission_extra_form = {
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
                "initial": agreement.pk,
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
            **DELETE_field,
        },
        "prefix": "commissions-__prefix__",
    }

    # Build commission forms
    commission_forms = []
    idx = None

    # append initial forms
    # only if any view perm
    if any_view_perm:
        for idx, commission in enumerate(commissions):
            if inline_change_perm:
                commission_forms.append(
                    {
                        "readonly_fields": {
                            "created_at": {
                                "type": "DateTimeField",
                                "value": commission.created_at.strftime(
                                    "%d/%m/%Y - %H:%M"
                                ),
                                "help_text": "",
                            },
                            "updated_at": {
                                "type": "DateTimeField",
                                "value": commission.updated_at.strftime(
                                    "%d/%m/%Y - %H:%M"
                                ),
                                "help_text": "",
                            },
                        },
                        "fields": {
                            "agreement": {
                                "type": "InlineForeignKeyField",
                                "label": "Agreement",
                                "required": False,
                                "help_text": "",
                                "initial": agreement.pk,
                            },
                            "beneficiary": {
                                "type": "ModelChoiceField",
                                "label": "Beneficiary",
                                "required": True,
                                "help_text": "",
                                "initial": {
                                    "value": commission.beneficiary.pk,
                                    "label": str(commission.beneficiary),
                                }
                                if commission.beneficiary_id
                                else None,
                                "model": "contact",
                                "app": "common",
                                "permissions": {
                                    "view": contacts_admin.has_view_permission(
                                        request, None
                                    ),
                                    "add": contacts_admin.has_add_permission(request),
                                    "change": contacts_admin.has_change_permission(
                                        request, None
                                    ),
                                    "delete": contacts_admin.has_delete_permission(
                                        request, None
                                    ),
                                },
                                "autocomplete": True,
                            },
                            "value": {
                                "type": "DecimalField",
                                "label": "Value",
                                "required": True,
                                "help_text": "",
                                "initial": commission.value,
                            },
                            "id": {
                                "type": "hidden",
                                "label": "pk",
                                "required": False,
                                "help_text": "",
                                "initial": commission.pk,
                            },
                            # appended only if delete perm
                            **DELETE_field,
                        },
                        "prefix": f"commissions-{idx}",
                    }
                )
            elif inline_view_perm:
                commission_forms.append(
                    {
                        "readonly_fields": {
                            "created_at": {
                                "type": "DateTimeField",
                                "value": commission.created_at.strftime(
                                    "%d/%m/%Y - %H:%M"
                                ),
                                "help_text": "",
                            },
                            "updated_at": {
                                "type": "DateTimeField",
                                "value": commission.updated_at.strftime(
                                    "%d/%m/%Y - %H:%M"
                                ),
                                "help_text": "",
                            },
                            "beneficiary": {
                                "type": "RelatedField",
                                "pk": commission.beneficiary.id
                                if commission.beneficiary
                                else None,
                                "model": "contact",
                                "app": "common",
                                "value": str(commission.beneficiary)
                                if commission.beneficiary
                                else None,
                                "help_text": "",
                                "permissions": {
                                    "view": contacts_admin.has_view_permission(
                                        request, commission.beneficiary
                                    ),
                                    "add": contacts_admin.has_add_permission(request),
                                    "change": contacts_admin.has_change_permission(
                                        request, commission.beneficiary
                                    ),
                                    "delete": contacts_admin.has_delete_permission(
                                        request, commission.beneficiary
                                    ),
                                },
                            },
                            "value": {
                                "type": "DecimalField",
                                "value": str(commission.value)
                                if commission.value
                                else "",
                                "help_text": "",
                            },
                        },
                        "fields": {
                            # these fields must be present even if only view perm
                            "id": {
                                "type": "hidden",
                                "label": "pk",
                                "required": False,
                                "help_text": "",
                                "initial": commission.id,
                            },
                            "agreement": {
                                "type": "InlineForeignKeyField",
                                "label": "Agreement",
                                "required": False,
                                "help_text": "",
                                "initial": commission.agreement.id,
                            },
                            # appended only if delete perm
                            **DELETE_field,
                        },
                        "prefix": f"commissions-{idx}",
                    }
                )

    # append extra forms
    # only if add perm
    if inline_add_perm:
        # --> inline has extra = 1
        extra_form = deepcopy(commission_extra_form)
        # if no view/change perm
        # user can only add
        # sees no other form
        extra_form["prefix"] = f"commissions-{0 if idx is None else idx+1}"
        commission_forms.append(extra_form)

    commissions_inline = {
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
        "management_form": {
            "fields": {
                "TOTAL_FORMS": {
                    "type": "IntegerField",
                    "label": None,
                    "required": True,
                    "help_text": "",
                    "initial": len(commission_forms),
                },
                "INITIAL_FORMS": {
                    "type": "IntegerField",
                    "label": None,
                    "required": True,
                    "help_text": "",
                    "initial": len(commissions) if any_view_perm else 0,
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
                    "initial": 0 if not inline_add_perm else 1000,
                },
            },
            "readonly_fields": {},
            "prefix": "commissions",
        },
        "forms": commission_forms,  # initial + extra forms
        "extra_form": commission_extra_form,
        "min_forms_num": 0,
        "max_forms_num": 0 if not inline_add_perm else 1000,
    }

    return {
        # ---------------------------------------------
        # object
        "object_repr": str(agreement),
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
            "type": {
                "type": "ChoiceField",
                "value": agreement.get_type_display(),
                "help_text": "type after creation gets locked",
            },
            "created_at": {
                "type": "DateTimeField",
                "value": agreement.created_at.strftime("%d/%m/%Y - %H:%M"),
                "help_text": "",
            },
            "updated_at": {
                "type": "DateTimeField",
                "value": agreement.updated_at.strftime("%d/%m/%Y - %H:%M"),
                "help_text": "",
            },
        },
        "fields": {
            "status": {
                "type": "TypedChoiceField",
                "label": "Status",
                "required": True,
                "help_text": "After setting to Agreed or Cancelled, <br>the Agreement gets locked and cannot be edited",
                "initial": str(agreement.status),
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
                "initial": agreement.agreement_signing_date.strftime("%Y-%m-%d")
                if agreement.agreement_signing_date
                else None,
            },
            "signing_time": {
                "type": "TimeField",
                "label": "Signing time",
                "required": False,
                "help_text": "",
                "initial": agreement.signing_time.strftime("%H:%M:%S")
                if agreement.signing_time
                else None,
            },
            "assigned_to": {
                "type": "ModelChoiceField",
                "label": "Assigned to",
                "required": False,
                "help_text": "",
                "initial": {
                    "value": agreement.assigned_to.pk,
                    "label": str(agreement.assigned_to),
                }
                if agreement.assigned_to
                else None,
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
                "initial": {
                    "value": agreement.project.pk,
                    "label": str(agreement.project.pk),
                }
                if agreement.project
                else None,
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
                "initial": {
                    "value": agreement.property_id,
                    "label": str(agreement.property),
                }
                if agreement.property_id
                else None,
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
                "initial": str(agreement.unique_id) if agreement.unique_id else None,
            },
            "website_url": {
                "type": "URLField",
                "label": "Website url",
                "required": False,
                "help_text": "",
                "initial": agreement.website_url,
            },
            "slug": {
                "type": "SlugField",
                "label": "Slug",
                "required": False,
                "help_text": "",
                "initial": agreement.slug,
            },
            "closure_percentage": {
                "type": "FloatField",
                "label": "Closure percentage",
                "required": False,
                "help_text": "",
                "initial": agreement.closure_percentage,
            },
            "agreement_int": {
                "type": "IntegerField",
                "label": "Agreement int",
                "required": False,
                "help_text": "needed an integer field",
                "initial": agreement.agreement_int,
            },
            "description": {
                "type": "TextField",
                "label": "Description",
                "required": False,
                "help_text": "",
                "initial": agreement.description,
                "rows": "10",
                "cols": "40",
            },
            "valid_from": {
                "type": "DateField",
                "label": "Valid from",
                "required": False,
                "help_text": "",
                "initial": agreement.valid_from.strftime("%Y-%m-%d")
                if agreement.valid_from
                else None,
            },
            "valid_until": {
                "type": "DateField",
                "label": "Valid until",
                "required": False,
                "help_text": "",
                "initial": agreement.valid_until.strftime("%Y-%m-%d")
                if agreement.valid_until
                else None,
            },
            "cancel_date": {
                "type": "DateField",
                "label": "Cancel date",
                "required": False,
                "help_text": "",
                "initial": agreement.cancel_date.strftime("%Y-%m-%d")
                if agreement.cancel_date
                else None,
            },
            "reservation_date": {
                "type": "DateField",
                "label": "Reservation date",
                "required": False,
                "help_text": "",
                "initial": agreement.reservation_date.strftime("%Y-%m-%d")
                if agreement.reservation_date
                else None,
            },
            "price": {
                "type": "DecimalField",
                "label": "Price",
                "required": False,
                "help_text": "",
                "initial": agreement.price,
            },
            "down_payment": {
                "type": "DecimalField",
                "label": "Down payment",
                "required": False,
                "help_text": "",
                "initial": str(agreement.down_payment)
                if agreement.down_payment
                else None,
            },
            "private_agreement_date": {
                "type": "DateField",
                "label": "Private agreement date",
                "required": False,
                "help_text": "",
                "initial": agreement.private_agreement_date.strftime("%Y-%m-%d")
                if agreement.private_agreement_date
                else None,
            },
        },
        "prefix": None,
        # ---------------------------------------------
        # inlines
        "inlines": [commissions_inline],
        # ---------------------------------------------
        # extra_data
        "extra_data": agreements_admin.get_edit_extra_data(request, agreement),
    }
