import urllib.parse

from django.contrib.admin import ListFilter
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import NestedObjects
from django.core.exceptions import FieldDoesNotExist
from django.db import router
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from .filters import InputFilter, AutocompleteFilter
from django.apps import apps
import logging

logger = logging.getLogger()


def get_list_filter_data(cl: ChangeList, spec: ListFilter):
    choices_ = list(spec.choices(cl))
    field_key = getattr(spec, "field_path", getattr(spec, "parameter_name", spec.title))
    matched_key = field_key

    if isinstance(spec, InputFilter):
        type_ = spec.field_type_str

    elif isinstance(spec, AutocompleteFilter):
        type_ = "autocomplete"

    elif isinstance(spec, ListFilter):
        type_ = "choice"

    for choice in choices_:
        qs = choice.get("query_string")
        if not qs:
            continue

        value = ""
        matches = {}
        query_parts = urllib.parse.parse_qs(qs[1:])
        for key in query_parts.keys():
            if key == field_key:
                value = query_parts[key][0]
                matched_key = key
            elif key.startswith(field_key + "__") or "__" + field_key + "__" in key:
                value = query_parts[key][0]
                matched_key = key

            if value:
                matches[matched_key] = value

        # Iterate matches, use original as actual values,
        # additional for hidden
        i = 0
        for key in matches:
            if i == 0:
                choice["name"] = key
                choice["value"] = matches[key]
            i += 1

    choices = [{"d": " - ", "v": None}]
    for c in choices_:
        if "display" in c and "value" in c:
            choices.append({"d": str(c["display"]), "v": str(c["value"])})

    if type_ == "choice":
        return {
            "type": type_,
            "field_name": field_key,
            "parameter_name": field_key,
            "disabled_by_default": getattr(spec, "disabled_by_default", False),
            "title": spec.title,
            #
            "choices": choices,
        }
    elif type_ == "autocomplete":
        return {
            "type": type_,
            "field_name": field_key,
            "parameter_name": field_key,
            "disabled_by_default": getattr(spec, "disabled_by_default", False),
            "title": spec.title,
            #
            "app_name": spec.related_model._meta.app_label,
            "model_name": spec.related_model._meta.model_name,
        }
    else:
        return {
            "type": type_, # "int", "float", "str", "date", "datetime"
            "field_name": field_key,
            "parameter_name": spec.parameter_name,
            "disabled_by_default": spec.disabled_by_default,
            "title": spec.title,
            #
            "choices": choices,
            "input_type": spec.input_type,  # html attr type
            "input_min": spec.input_min,  # html attr min
            "input_max": spec.input_max,  # html attr max
            "step": spec.step,  # html attr step
            "placeholder": spec.placeholder,  # html attr placeholder
        }


def get_deleted_objects(objs, request, admin_site):
    """
    Find all objects related to `objs` that should also be deleted. `objs`
    must be a homogeneous iterable of objects (e.g. a QuerySet).

    Return a nested list of strings suitable for display in the
    template with the ``unordered_list`` filter.

    WARNING:
    permissions are not checked for m2m through models
    that do not have a `ModelAdmin` registered
    """
    try:
        obj = objs[0]
    except IndexError:
        return [], {}, set(), []
    else:
        using = router.db_for_write(obj._meta.model)

    collector = NestedObjects(using=using, origin=objs)
    collector.collect(objs)

    perms_needed = set()

    def format_callback(obj):
        model = obj.__class__
        has_admin = model in admin_site._registry
        opts = obj._meta
        if has_admin:
            if not admin_site._registry[model].has_delete_permission(request, obj):
                perms_needed.add(opts.verbose_name)
            return mark_safe(
                f'<a href="/{model._meta.app_label}/{model._meta.model_name}/{obj.pk}/">{obj}</a>'
            )
        else:
            return "%s: %s" % (capfirst(opts.verbose_name), obj)

    to_delete = collector.nested(format_callback)
    # to_delete can have the form:
    # [
    #   '<a href="/real_estate/property/1/">asd</a>',
    #   [
    #       'property owner str',
    #       'property contact str',
    #   ]
    # ]

    protected = [format_callback(obj) for obj in collector.protected]

    model_count = {
        model._meta.verbose_name_plural: len(objs)
        for model, objs in collector.model_objs.items()
    }

    return to_delete, model_count, perms_needed, protected
