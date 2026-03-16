from django.contrib.admin import site
from django.utils.text import capfirst
from backend.real_estate import models as real_estate_models
from .common import DummyRequest


def get_object_delete_data(user, prop):
    """
    Get the object delete data for an object.
    Replicates what the view should return.
    It is essential part of the testing process.

    ARGS:
        user: The user to generate view data for
        prop: The object instance to generate delete data for

    RETURNS:
        Dictionary containing the object delete data
    """
    request = DummyRequest(user)

    agreements_admin = site._registry[real_estate_models.Agreement]
    properties_admin = site._registry[real_estate_models.Property]

    connected_agreements = prop.agreements.all()
    property_owners = prop.property_owners.all()
    property_contacts = real_estate_models.PropertyAssociatedContact.objects.filter(
        property=prop
    )

    if connected_agreements:
        perms_needed = (
            ["agreement"]
            if not agreements_admin.has_delete_permission(request, prop)
            else []
        )
        protected = [
            f'<a href="/real_estate/agreement/{a.pk}/">{a}</a>'
            for a in connected_agreements
        ]
    else:
        perms_needed = []
        protected = []

    to_delete = [f'<a href="/real_estate/property/{prop.pk}/">{prop}</a>']
    model_count = {"Properties": "1"}

    # ------------
    # property owner/contacts
    # do not have a `ModelAdmin` registered
    # so strings are returned, and not html links
    if property_contacts and not property_owners:
        to_delete.append(
            ["%s: %s" % (capfirst(pc._meta.verbose_name), pc) for pc in property_contacts]
        )
        model_count["Property Contacts"] = str(len(property_contacts))

    elif property_owners and not property_contacts:
        to_delete.append(
            ["%s: %s" % (capfirst(po._meta.verbose_name), po) for po in property_owners]
        )
        model_count["Property Owners"] = str(len(property_owners))

    elif property_contacts and property_owners:
        po_objs = [
            "%s: %s" % (capfirst(po._meta.verbose_name), po) for po in property_owners
        ]
        pc_objs = [
            "%s: %s" % (capfirst(pc._meta.verbose_name), pc) for pc in property_contacts
        ]
        to_delete.append(pc_objs + po_objs)
        model_count["Property Contacts"] = str(len(property_contacts))
        model_count["Property Owners"] = str(len(property_owners))

    # ------------
    return {
        "object_repr": str(prop),
        "permissions": {
            "view": True,
            "delete": not protected and not perms_needed,
        },
        "deleted_objects": to_delete,
        "model_count": model_count,
        "perms_needed": tuple(perms_needed),
        "protected": tuple(protected),
        # extra_data
        "extra_data": properties_admin.get_delete_extra_data(request, prop),
    }
