from django.contrib.admin import site
from backend.real_estate import models as real_estate_models
from backend.common import models as common_models
from backend.organization import models as organization_models
from .common import DummyRequest


def get_object_view_data(agreement, user):
    """
    Get the object view data for an agreement object.
    Replicates what the view should return.

    ARGS:
        agreement: The agreement instance to generate view data for
        user: The user to generate view data for

    RETURNS:
        Dictionary containing the object view data
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
    inline_view_perm = user.has_perm("real_estate.view_agreementcommission")
    any_view_perm = inline_view_perm or inline_change_perm

    view_history_perm = (
        agreements_admin.has_view_history_permission(request, agreement)
        if hasattr(agreements_admin, "has_view_history_permission")
        else True
    )

    agreement_commisions = agreement.commissions.all()

    if any_view_perm:
        inlines = [
            {
                "type": "tabular",
                "label": "Commissions",
                "app": "real_estate",
                "model": "agreementcommission",
                "objects": [
                    {
                        "beneficiary": {
                            "type": "RelatedField",
                            "pk": ac.beneficiary.pk,
                            "model": "contact",
                            "app": "common",
                            "value": str(ac.beneficiary),
                            "help_text": "",
                            "permissions": {
                                "view": contacts_admin.has_view_permission(
                                    request, ac.beneficiary
                                ),
                                "add": contacts_admin.has_add_permission(request),
                                "change": contacts_admin.has_change_permission(
                                    request, ac.beneficiary
                                ),
                                "delete": contacts_admin.has_delete_permission(
                                    request, ac.beneficiary
                                ),
                            },
                        },
                        "value": {
                            "type": "DecimalField",
                            "value": str(ac.value) if ac.value else "",
                            "help_text": "",
                        },
                        "created_at": {
                            "type": "DateTimeField",
                            "value": ac.created_at.strftime("%d/%m/%Y - %H:%M"),
                            "help_text": "",
                        },
                        "updated_at": {
                            "type": "DateTimeField",
                            "value": ac.updated_at.strftime("%d/%m/%Y - %H:%M"),
                            "help_text": "",
                        },
                        "pk": {
                            "type": "IntegerField",
                            "value": ac.pk,
                            "help_text": "",
                        },
                    }
                    for ac in agreement_commisions
                ],
                "all_fieldnames": ["beneficiary", "value", "created_at", "updated_at"],
            }
        ]
    elif inline_add_perm or inline_delete_perm:
        inlines = [
            {
                "type": "tabular",
                "label": "Commissions",
                "app": "real_estate",
                "model": "agreementcommission",
                "objects": [],
                "all_fieldnames": ["beneficiary", "value", "created_at", "updated_at"],
            }
        ]
    else:
        inlines = []

    return {
        "object_repr": str(agreement),
        #
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
        #
        "object": {
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
            "type": {
                "type": "ChoiceField",
                "value": agreement.get_type_display(),
                "help_text": "type after creation gets locked",
            },
            "status": {
                "type": "ChoiceField",
                "value": agreement.get_status_display(),
                "help_text": "After setting to Agreed or Cancelled, <br>the Agreement gets locked and cannot be edited",
            },
            "agreement_signing_date": {
                "type": "DateField",
                "value": agreement.agreement_signing_date.strftime("%d/%m/%Y")
                if agreement.agreement_signing_date
                else None,
                "help_text": "If a date is provided, the agreement will be thought as accepted. <br>This will lock the agreement for edit.",
            },
            "signing_time": {
                "type": "TimeField",
                "value": agreement.signing_time.strftime("%H:%M")
                if agreement.signing_time
                else None,
                "help_text": "",
            },
            "assigned_to": {
                "type": "RelatedField",
                "pk": agreement.assigned_to.id if agreement.assigned_to else None,
                "model": "user",
                "app": "organization",
                "value": str(agreement.assigned_to) if agreement.assigned_to else None,
                "help_text": "",
                "permissions": {
                    "view": users_admin.has_view_permission(
                        request, agreement.assigned_to
                    ),
                    "add": users_admin.has_add_permission(request),
                    "change": users_admin.has_change_permission(
                        request, agreement.assigned_to
                    ),
                    "delete": users_admin.has_delete_permission(
                        request, agreement.assigned_to
                    ),
                },
            },
            "project": {
                "type": "RelatedField",
                "pk": agreement.project.id if agreement.project else None,
                "app": "real_estate",
                "model": "project",
                "value": str(agreement.project) if agreement.project else None,
                "help_text": "",
                "permissions": {
                    "view": projects_admin.has_view_permission(
                        request, agreement.project
                    ),
                    "add": projects_admin.has_add_permission(request),
                    "change": projects_admin.has_change_permission(
                        request, agreement.project
                    ),
                    "delete": projects_admin.has_delete_permission(
                        request, agreement.project
                    ),
                },
            },
            "property": {
                "type": "RelatedField",
                "pk": agreement.property.id if agreement.property else None,
                "model": "property",
                "app": "real_estate",
                "value": str(agreement.property) if agreement.property else None,
                "help_text": "",
                "permissions": {
                    "view": properties_admin.has_view_permission(
                        request, agreement.property
                    ),
                    "add": properties_admin.has_add_permission(request),
                    "change": properties_admin.has_change_permission(
                        request, agreement.property
                    ),
                    "delete": properties_admin.has_delete_permission(
                        request, agreement.property
                    ),
                },
            },
            "unique_id": {
                "type": "UUIDField",
                "value": agreement.unique_id if agreement.unique_id else "",
                "help_text": "",
            },
            "website_url": {
                "type": "URLField",
                "value": agreement.website_url if agreement.website_url else "",
                "help_text": "",
            },
            "slug": {
                "type": "SlugField",
                "value": agreement.slug if agreement.slug else "",
                "help_text": "",
            },
            "closure_percentage": {
                "type": "FloatField",
                "value": agreement.closure_percentage,
                "help_text": "",
            },
            "agreement_int": {
                "type": "IntegerField",
                "value": agreement.agreement_int,
                "help_text": "needed an integer field",
            },
            "description": {
                "type": "TextField",
                "value": agreement.description,
                "help_text": agreement._meta.get_field("description").help_text,
            },
            "valid_from": {
                "type": "DateField",
                "value": agreement.valid_from.strftime("%d/%m/%Y")
                if agreement.valid_from
                else None,
                "help_text": agreement._meta.get_field("valid_from").help_text,
            },
            "valid_until": {
                "type": "DateField",
                "value": agreement.valid_until.strftime("%d/%m/%Y")
                if agreement.valid_until
                else None,
                "help_text": agreement._meta.get_field("valid_until").help_text,
            },
            "cancel_date": {
                "type": "DateField",
                "value": agreement.cancel_date.strftime("%d/%m/%Y")
                if agreement.cancel_date
                else None,
                "help_text": agreement._meta.get_field("cancel_date").help_text,
            },
            "reservation_date": {
                "type": "DateField",
                "value": agreement.reservation_date.strftime("%d/%m/%Y")
                if agreement.reservation_date
                else None,
                "help_text": agreement._meta.get_field("reservation_date").help_text,
            },
            "price": {
                "type": "DecimalField",
                "value": str(agreement.price) if agreement.price else "",
                "help_text": agreement._meta.get_field("price").help_text,
            },
            "down_payment": {
                "type": "DecimalField",
                "value": str(agreement.down_payment) if agreement.down_payment else "",
                "help_text": agreement._meta.get_field("down_payment").help_text,
            },
            "private_agreement_date": {
                "type": "DateField",
                "value": agreement.private_agreement_date.strftime("%d/%m/%Y")
                if agreement.private_agreement_date
                else None,
                "help_text": agreement._meta.get_field(
                    "private_agreement_date"
                ).help_text,
            },
            "pk": {
                "type": "IntegerField",
                "value": agreement.pk,
                "help_text": agreement._meta.get_field("id").help_text,
            },
        },
        #
        "permissions": {
            "view": agreements_admin.has_view_permission(request, agreement),
            "add": agreements_admin.has_add_permission(request),
            "change": agreements_admin.has_change_permission(request, agreement),
            "delete": agreements_admin.has_delete_permission(request, agreement),
            "history": view_history_perm,
        },
        #
        "inlines": inlines,
        #
        "extra_data": agreements_admin.get_view_extra_data(request, agreement),
    }
