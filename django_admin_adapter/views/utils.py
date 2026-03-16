import json

from django import forms
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import InlineForeignKeyField, ModelForm
from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from ..serializers.object import AdminObjectViewSerializer


# formats recognized by the browsers
# to this format the date/datetime/time
# field value will be formatted
DATE_FIELD_STR_FORMAT = "%Y-%m-%d"
DATETIME_FIELD_STR_FORMAT = "%Y-%m-%dT%H:%M:%S"
TIME_FIELD_STR_FORMAT = "%H:%M"


def build_form_field_data(
    fieldname: str,
    form: ModelForm,
    model_admin: admin.ModelAdmin = None,
    request: HttpRequest = None,
    is_inline: bool = False,
    admin_site: admin.AdminSite = None,
):
    """
    Receives params and returns
    data describing the form field to be created
    in the front-end.

    RETURNS:
        {
            "type": str (FormField class name),
            "label": str,
            "required": bool,
            "help_text": str,
            "initial": varying,
            (extra fields for special cases)
        }
    """
    model = model_admin.model if model_admin else None
    formfield = form.fields[fieldname]

    field_class_name = formfield.__class__.__name__
    field = {
        "type": field_class_name,
        "label": formfield.label,
        "required": formfield.required,
        "help_text": formfield.help_text,
    }
    initial = (
        form.initial[fieldname] if fieldname in form.initial else getattr(formfield, "initial")
    )
    field["initial"] = initial

    # -------- ChoiceField, TypedChoiceField --------
    if field_class_name in ("ChoiceField", "TypedChoiceField"):
        field["choices"] = formfield.choices

    # -------- TextField --------
    elif field_class_name == "CharField" and isinstance(formfield.widget, forms.Textarea):
        field["type"] = "TextField"
        field["rows"] = formfield.widget.attrs.get("rows", 3)
        field["cols"] = formfield.widget.attrs.get("cols", 10)

    # -------- DateField --------
    elif field_class_name == "DateField" and initial:
        if callable(initial):
            field["initial"] = initial().strftime(DATE_FIELD_STR_FORMAT)
        else:
            field["initial"] = initial.strftime(DATE_FIELD_STR_FORMAT)

    # -------- DateTimeField --------
    elif field_class_name == "DateTimeField" and initial:
        if callable(initial):
            field["initial"] = initial().strftime(DATETIME_FIELD_STR_FORMAT)
        else:
            field["initial"] = initial.strftime(DATETIME_FIELD_STR_FORMAT)

    # -------- TimeField --------
    elif field_class_name == "TimeField" and initial:
        if callable(initial):
            field["initial"] = initial().strftime(TIME_FIELD_STR_FORMAT)
        else:
            field["initial"] = initial.strftime(TIME_FIELD_STR_FORMAT)

    # -------- JSONField --------
    elif field_class_name == "JSONField":
        if callable(initial):
            field["initial"] = json.dumps(initial())
        else:
            field["initial"] = json.dumps(initial)

        field["rows"] = formfield.widget.attrs.get("rows", 4)
        field["cols"] = formfield.widget.attrs.get("cols", 10)

    # -------- ModelChoiceField --------
    elif field_class_name == "ModelChoiceField":
        # get the related model
        # from the source field
        source_field = model._meta.get_field(fieldname)
        remote_model = source_field.remote_field.model
        to_field_name = getattr(
            source_field.remote_field, "field_name", remote_model._meta.pk.attname
        )
        to_field_name = remote_model._meta.get_field(to_field_name).attname

        field["model"] = remote_model._meta.model_name
        field["app"] = remote_model._meta.app_label

        remote_model_admin = admin_site._registry.get(remote_model)
        if remote_model_admin is None:
            field["permissions"] = {
                "view": False,
                "add": False,
                "change": False,
                "delete": False,
            }
        else:
            obj = form.instance # if change else None

            field["permissions"] = {
                "view": remote_model_admin.has_view_permission(request, obj),
                "add": remote_model_admin.has_add_permission(request),
                "change": remote_model_admin.has_change_permission(request, obj),
                "delete": remote_model_admin.has_delete_permission(request, obj),
            }

        # if not autocomplete field,
        # pass the queyset as choices

        if model_admin is not None and fieldname in model_admin.get_autocomplete_fields(
            request
        ):
            field["autocomplete"] = True
        else:
            field["autocomplete"] = False
            field["choices"] = [
                {"value": getattr(obj, to_field_name), "label": str(obj)}
                for obj in formfield.queryset
            ]
            # handle nullable case
            if source_field.null or is_inline:
                field["choices"].insert(0, {"value": "", "label": "-"})

        # pass default/initial choices
        if initial:
            try:
                remote_object = remote_model.objects.get(**{to_field_name: initial})
                field["initial"] = {
                    "value": getattr(remote_object, to_field_name),
                    "label": str(remote_object),
                }
            except ObjectDoesNotExist:
                pass

    # -------- ModelMultipleChoiceField --------
    elif field_class_name == "ModelMultipleChoiceField":
        field["initial"] = [obj.pk for obj in initial] if initial else []
        field["choices"] = [{"value": obj.pk, "label": str(obj)} for obj in formfield.queryset]

    # -------- ImageField , FileField --------
    elif field_class_name in ("ImageField", "FileField"):
        try:
            initial = form.initial[fieldname].url
            field["initial"] = initial
        except (KeyError, ValueError):
            field["initial"] = None

    return field


def build_form_data(
    request: HttpRequest,
    model_admin: admin.ModelAdmin,
    form: ModelForm,
    readonly_fields: list|tuple,
    pk_name: str|None = None, # for inline forms
    object_serializer_class=None,
    admin_site: admin.AdminSite = None,
):
    """
    RETURNS:
    {
        "readonly_fields": {
            "fieldname": readonly_field_data,
            ...
        },
        #
        "fields": {
            "fieldname": form_field_data,
            ...
        },
        #
        "prefix": str(form.prefix),
    }
    """
    fields_data = {}

    # ---- fields:
    if (
        pk_name is not None and
        pk_name in form.fields
    ):
        fields_data[pk_name] = {
            "type": "hidden",
            "label": "pk",
            "required": False,
            "help_text": "",
            "initial": form.initial[pk_name]
            if pk_name in form.initial
            else getattr(form.fields[pk_name], "initial"),
        }
        del form.fields[pk_name]

    for fieldname in form.fields:
        if fieldname in readonly_fields:
            # this check is made
            # for inline forms
            continue
        fields_data[fieldname] = build_form_field_data(
            fieldname=fieldname,
            form=form,
            model_admin=model_admin,
            request=request,
            is_inline=True,
            admin_site=admin_site,
        )

    # ---- readonly_fields:
    readonly_fields_data = object_serializer_class(
        form.instance,
        model_class=model_admin.model,
        all_fields=readonly_fields,
        context={
            "model_admin": model_admin,
            "request": request,
            "admin_site": admin_site,
        },
        ignore_pk=True,
    ).data


    return {
        "readonly_fields": readonly_fields_data,
        "fields": fields_data,
        "prefix": form.prefix,
    }


# ----------------------------------
#
# ---- INLINE HELPERS
#
# ---- functions for helping create the data
# ---- that are needed for the UI
# ---- to display the readonly fields
# ---- and create the inputs for inlines
# ---- in order to render the forms correctly
#
# ----------------------------------


def build_inline_data(
    request,
    parent_obj,
    inline_instance,
    formset,
    object_serializer_class,
    admin_site=None,
    change=False,
):
    pk_name = inline_instance.model._meta.pk.attname

    can_change = inline_instance.has_change_permission(request, parent_obj)

    # ----------------------------------------
    # -------- create the management form
    # ----------------------------------------
    management_form = {
        "fields": {
            fieldname: build_form_field_data(
                fieldname=fieldname,
                form=formset.management_form,
                model_admin=None,
                request=request,
            )
            for fieldname in formset.management_form.fields
        },
        "readonly_fields": {},
        "prefix": formset.management_form.prefix,
    }

    # ----------------------------------------
    # -------- get readonly fields
    # ----------------------------------------
    readonly_fields = list(inline_instance.get_readonly_fields(request, parent_obj))
    excluded = inline_instance.get_exclude(request, parent_obj)
    exclude = [] if excluded is None else list(excluded)
    for f in exclude:
        if f not in readonly_fields:
            readonly_fields.append(f)
    if excluded is None and hasattr(inline_instance.form, "_meta") and inline_instance.form._meta.exclude:
        # Take the custom ModelForm's Meta.exclude into account
        # ONLY if the InlineModelAdmin doesn't define its own.
        exclude.extend(inline_instance.form._meta.exclude)
        for f in inline_instance.form._meta.exclude:
            if f not in readonly_fields:
                readonly_fields.append(f)

    # ----------------------------------------
    # -------- create the extra form
    # ----------------------------------------
    extra_form = build_form_data(
        request=request,
        model_admin=inline_instance,
        form=formset.empty_form,
        readonly_fields=readonly_fields,
        pk_name=pk_name,
        object_serializer_class=object_serializer_class,
        admin_site=admin_site,
    )

    # ----------------------------------------
    # -------- create the inline forms
    # ----------------------------------------
    if change:
        # in case of no change permission
        # the initial forms cannot be changed
        # so we mark all fields as readonly
        # EXCEPT `pk_name` ,`DELETE` and `inline_related_field`
        # -------- @ -------- @ -------- @ -------- @
        # this logic is replicated form `get_inline_formsets`
        # and `helpers.InlineAdminFormSet`
        # -------- @ -------- @ -------- @ -------- @
        # FOR CHANGE :
        # even if html is tampered before submit
        # in `_create_formsets` for the initial forms
        # `cleaned_data` are appended as the `initial_data`!!
        # in case of no change perm
        # -------- @ -------- @ -------- @ -------- @
        # FOR DELETE :
        # also in case of tampered DELETE field
        # if no delete permission
        # admin does not append the DELETE field
        # in the initial forms - so it doesn't work
        # -------- @ -------- @ -------- @ -------- @
        # in all cases, admin always sends
        # the pk and inline related fields
        # -------- @ -------- @ -------- @ -------- @

        init_form_ro_fields = readonly_fields.copy()

        if not can_change:
            # make all fields readonly
            # EXCEPT `pk_name` ,`DELETE` and `inline_related_field`
            empty_form = formset.empty_form
            formfields = list(empty_form.fields)

            for fieldname in empty_form.fields:
                # remove inline related field (inline foreign field)
                # must always send it
                if isinstance(empty_form.fields[fieldname], InlineForeignKeyField):
                    formfields.remove(fieldname)
                    break

            if pk_name in formfields:
                # remove pk field
                # must always send it
                formfields.remove(pk_name)

            if "DELETE" in formfields:
                formfields.remove("DELETE")

            for f in formfields:
                if f not in init_form_ro_fields:
                    init_form_ro_fields.append(f)

        initial_inline_forms = [
            build_form_data(
                request,
                inline_instance,
                inline_form,
                # SOS: initial RO fields
                # that MAY differ due to
                # user change permission
                init_form_ro_fields,
                pk_name,
                object_serializer_class=object_serializer_class,
                admin_site=admin_site,
            )
            for inline_form in formset.initial_forms
        ]
        extra_inline_forms = [
            build_form_data(
                request,
                inline_instance,
                inline_form,
                readonly_fields,
                pk_name,
                object_serializer_class=object_serializer_class,
                admin_site=admin_site,
            )
            for inline_form in formset.extra_forms
        ]
        inline_forms = initial_inline_forms + extra_inline_forms
    else:
        # in case of add, the inline
        # will be added only if
        # user has add perm
        inline_forms = [
            build_form_data(
                request,
                inline_instance,
                form,
                readonly_fields,
                pk_name,
                object_serializer_class=object_serializer_class,
                admin_site=admin_site,
            )
            for form in formset.forms
        ]
    # ----------------------------------------
    return {
        "type": "tabular" if isinstance(inline_instance, admin.TabularInline) else "stacked",
        "label": inline_instance.verbose_name_plural or inline_instance.model._meta.verbose_name_plural,
        "model": inline_instance.model._meta.model_name,
        "app": inline_instance.model._meta.app_label,
        #
        "permissions": {
            "view": inline_instance.has_view_permission(request, parent_obj),
            "add": inline_instance.has_add_permission(request, parent_obj),
            "change": can_change,
            "delete": inline_instance.has_delete_permission(request, parent_obj),
        },
        #
        "pk_name": pk_name,
        "prefix": formset.prefix,
        "management_form": management_form,
        "forms": inline_forms,
        "extra_form": extra_form,
        "min_forms_num": min(formset.min_num, formset.max_num),
        "max_forms_num": formset.max_num,
    }


def build_object_error_response(form, formsets):
    inlines_error_data = {}

    for _, formset in enumerate(formsets):
        inlines_error_data[formset.prefix] = {
            "forms_errors": formset.errors,
            # this is html <ul>
            "non_forms_errors": formset._non_form_errors.get_json_data(),
        }

    return Response(
        data={
            "error_data": form.errors.get_json_data(escape_html=False),
            "inlines_error_data": inlines_error_data,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )
