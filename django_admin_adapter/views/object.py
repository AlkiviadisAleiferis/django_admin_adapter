from django.contrib.admin.utils import flatten_fieldsets
from django.db import transaction
from django.contrib import admin
from django.forms.models import _get_foreign_key
from django.forms.formsets import all_valid
from rest_framework.response import Response
from rest_framework import status
from ..serializers.list import AdminListSerializer
from ..utils import get_deleted_objects
from .base import BaseAdminAPIView, BaseAdminObjectAPIView
from .utils import (
    build_form_data,
    build_inline_data,
    build_object_error_response,
)


# % ---------------- Functional Object API Views ----------------


class AdminObjectAPIView(BaseAdminObjectAPIView):
    """
    API View implementing:
        - retrieve (GET) base object data
        - update (PUT) object
        - delete (DELETE) object
    """

    def delete(self, request, *args, **kwargs):
        if self.obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        can_delete = self.model_admin.has_delete_permission(request, self.obj)

        if not can_delete:
            return Response(status=status.HTTP_403_FORBIDDEN)

        (
            deleted_objects,
            model_count,
            perms_needed,
            protected,
        ) = self.model_admin.get_deleted_objects([self.obj], request)

        if perms_needed or protected:
            return Response(status=status.HTTP_403_FORBIDDEN)

        obj_repr = str(self.obj)
        self.model_admin.log_deletion(request, self.obj, obj_repr)
        self.model_admin.delete_model(request, self.obj)

        return Response(
            data={"messages": [f"The object {obj_repr} was deleted successfully."]},
            # TODO: should be 204 but axios drops response data
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        # % ----------- case where object is not found -----------
        if self.obj is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )

        can_change = self.model_admin.has_change_permission(request, self.obj)

        # % ----------- case where no change permission -----------
        if not can_change:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():
            fieldsets = self.model_admin.get_fieldsets(request, self.obj)
            fieldnames = flatten_fieldsets(fieldsets)
            ModelForm = self.model_admin.get_form(
                request, self.obj, change=True, fields=fieldnames
            )
            request.method = "POST"
            # in DRF, even if the request method is PUT,
            # the request is initialized with data in request.POST
            form = ModelForm(request.POST, request.FILES, instance=self.obj)
            formsets, inline_instances = self.model_admin._create_formsets(
                request,
                self.obj,
                change=True,
            )

            form_validated = form.is_valid()

            if form_validated:
                updated_object = self.model_admin.save_form(request, form, change=True)
            else:
                updated_object = form.instance

            if all_valid(formsets) and form_validated:
                self.model_admin.save_model(request, updated_object, form, True)
                self.model_admin.save_related(request, form, formsets, True)

                change_message = self.model_admin.construct_change_message(
                    request, form, formsets, False
                )
                self.model_admin.log_change(request, updated_object, change_message)
                return Response(
                    data={"messages": [f"{updated_object} updated successfully."]},
                    status=status.HTTP_200_OK,
                )

            else:
                return build_object_error_response(form, formsets)


# ------- UI views -------


class AdminObjectViewAPIView(BaseAdminObjectAPIView):
    """
    Returns the data necessary to construct
    the object view UI.
    This data includes:
        - field information
        - UI info (fieldsets, readonly fields)
        - permissions
        - inline configurations
    """

    def get(self, request, *args, **kwargs):
        # ---------------------------------------------
        # % ----------- case where object is not found
        # ---------------------------------------------
        if self.obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        can_view = self.model_admin.has_view_or_change_permission(request, self.obj)

        # ---------------------------------------------
        # % ----------- case where no view permission
        # ---------------------------------------------
        if not can_view:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # ---------------------------------------------
        can_change = self.model_admin.has_change_permission(request, self.obj)
        can_add = self.model_admin.has_add_permission(request)
        can_delete = self.model_admin.has_delete_permission(request, self.obj)
        history_perm_method = getattr(self.model_admin, "has_history_permission", None)
        can_view_history = history_perm_method(request, self.obj) if history_perm_method else True

        # ---------------------------------------------
        fieldsets = self.model_admin.get_fieldsets(request, self.obj)

        # ---------------------------------------------
        object_data = self._adapter_instance.object_serializer_class(
            self.obj,
            model_class=self.model,
            all_fields=flatten_fieldsets(fieldsets),
            context={
                "model_admin": self.model_admin,
                "request": request,
                "admin_site": self._admin_site,
            },
        ).data

        # ---------------------------------------------
        inlines = []

        for inline_instance in self.model_admin.get_inline_instances(request, self.obj):
            obj = self.obj
            fieldnames = flatten_fieldsets(inline_instance.get_fieldsets(request, obj))

            foreign_key_field = _get_foreign_key(
                inline_instance.parent_model,
                inline_instance.model,
                inline_instance.fk_name,
            )
            fk_name = foreign_key_field.name

            if fk_name in fieldnames:
                fieldnames.remove(fk_name)

            # if no VIEW or CHANGE permission
            # but with ADD and/or DELETE permission
            # this qs will be queryset.none()
            # inline will be provided, but with no objects
            qs = inline_instance.get_queryset(request).filter(**{fk_name: obj})

            objects = [
                self._adapter_instance.object_serializer_class(
                    inline_obj,
                    model_class=inline_instance.model,
                    all_fields=fieldnames,
                    context={
                        "model_admin": inline_instance,
                        "request": request,
                        "admin_site": self._admin_site,
                    },
                ).data
                for inline_obj in qs
            ]
            inlines.append(
                {
                    "type": "tabular" if isinstance(inline_instance, admin.TabularInline) else "stacked",
                    "label": inline_instance.verbose_name_plural,
                    "model": inline_instance.model._meta.model_name,
                    "app": inline_instance.model._meta.app_label,
                    "objects": objects,
                    "all_fieldnames": fieldnames,
                }
            )

        # ---------------------------------------------
        if hasattr(self.model_admin, "get_view_extra_data"):
            extra_data = self.model_admin.get_view_extra_data(request, self.obj)
        else:
            extra_data = None

        # ---------------------------------------------
        return Response(
            data={
                "object_repr": str(self.obj),
                "fieldsets": fieldsets,
                # ----
                "object": object_data,
                # ----
                "permissions": {
                    "view": can_view,
                    "add": can_add,
                    "change": can_change,
                    "delete": can_delete,
                    #
                    "history": can_view_history,
                },
                # ----
                "inlines": inlines,
                # ----
                "extra_data": extra_data,
            },
            status=status.HTTP_200_OK,
        )


class BaseObjectUIAPIView:
    """
    Base API View for Object UI.
    Responsible for returning the
    following UI data for the
    edit and add views:

        {
            "object_repr": str|None,
            "model": str,
            "app": str,
            "fieldsets": [
                (
                    None,
                    {
                        "fields": list|tuple[str],
                        "classes": list|tuple[str],
                        "description": str|None,
                    },
                )
            ],
            # --------
            # form_data
            # --------
            "readonly_fields": readonly_fields,
            "fields": {
                str: {
                    "type": str,
                    "label": str,
                    "required": bool,
                    "help_text": str,
                    "initial": any,
                    #
                    "choices": list|tuple[
                        tuple[str, str],
                    ],
                    "model": str,
                    "app": str,
                    "permissions": {
                        "view": bool,
                        "add": bool,
                        "change": bool,
                        "delete": bool,
                    },
                    "autocomplete": bool,
                    #
                    "cols": int,
                    "rows": int,

            },
            "prefix": str,
            # --------
            # inlines
            # --------
            "inlines": [
                {
                    "type": str,
                    "label": str,
                    "model": str,
                    "app": str,
                    #
                    "permissions": {
                        "view": bool,
                        "add": bool,
                        "change": bool,
                        "delete": bool,
                    },
                    #
                    "pk_name": str,
                    "prefix": str,
                    "management_form": form_data,
                    "forms": [
                        form_data,
                        ..
                    ],
                    "extra_form": form_data,
                    "min_forms_num": int,
                    "max_forms_num": int,
                }
            ],
        }
    """

    def get(self, request, change=False, obj=None, *args, **kwargs):
        fieldsets = self.model_admin.get_fieldsets(request, obj)

        # ---------------------------------------------
        # -------- create main object's form data
        # ---------------------------------------------
        # try to keep the order of the
        # readonly_fields, as provided
        # by the admin method
        readonly_fields = list(self.model_admin.get_readonly_fields(request, obj))
        excluded = self.model_admin.get_exclude(request, obj)
        exclude = [] if excluded is None else list(excluded)
        for f in exclude:
            if f not in readonly_fields:
                readonly_fields.append(f)

        ModelForm = self.model_admin.get_form(
            request,
            obj,
            change=change,
            fields=flatten_fieldsets(fieldsets),
            # `get_form` uses the `readonly_fields`
            # when creating the form
        )

        if change:
            form = ModelForm(instance=obj)
        else:
            initial = self.model_admin.get_changeform_initial_data(request)
            form = ModelForm(initial=initial)

        form_data = build_form_data(
            request=request,
            model_admin=self.model_admin,
            form=form,
            readonly_fields=readonly_fields,
            object_serializer_class=self._adapter_instance.object_serializer_class,
            admin_site=self._admin_site,
        )

        # ---------------------------------------------
        # -------- create all the inlines data
        # ---------------------------------------------
        formsets, inline_instances = self.model_admin._create_formsets(
            request, obj, change=change,
        )

        inlines_data = [
            build_inline_data(
                request=request,
                parent_obj=obj,
                inline_instance=inline_instances[i],
                formset=formset,
                object_serializer_class=self._adapter_instance.object_serializer_class,
                admin_site=self._admin_site,
                change=change,
            )
            for i, formset in enumerate(formsets)
        ]

        # ---------------------------------------------
        # -------- extra_data
        # ---------------------------------------------
        extra_data = None

        if change and hasattr(self.model_admin, "get_edit_extra_data"):
            extra_data = self.model_admin.get_edit_extra_data(request, obj)
        elif not change and hasattr(self.model_admin, "get_add_extra_data"):
            extra_data = self.model_admin.get_add_extra_data(request)

        # ---------------------------------------------
        return Response(
            data={
                "object_repr": str(obj) if obj is not None else None,
                "model": self.model._meta.model_name,
                "app": self.model._meta.app_label,
                "fieldsets": fieldsets,
                # ----
                # form
                # ----
                **form_data,
                # ----
                # inlines
                # ----
                "inlines": inlines_data,
                # ----
                "extra_data": extra_data,
            },
            status=status.HTTP_200_OK,
        )


class AdminObjectAddAPIView(BaseObjectUIAPIView, BaseAdminAPIView):
    """
    API View returning the data
    to build the Add View in the front-end.
    """

    def get(self, request, *args, **kwargs):
        # ---------------------------------------------
        # ----------- case where no add permission
        # ---------------------------------------------
        can_add = self.model_admin.has_add_permission(request)

        if not can_add:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().get(request, change=False, obj=None, *args, **kwargs)


class AdminObjectEditAPIView(BaseObjectUIAPIView, BaseAdminObjectAPIView):
    """
    API View returning the data
    to build the Edit View in the front-end.
    """

    def get(self, request, *args, **kwargs):
        # ---------------------------------------------
        # ----------- case where object is not found
        # ---------------------------------------------
        if self.obj is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )

        # ---------------------------------------------
        # ----------- case where no change permission
        # ---------------------------------------------
        can_change = self.model_admin.has_change_permission(request, self.obj)

        if not can_change:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().get(request, change=True, obj=self.obj, *args, **kwargs)


class AdminObjectConfirmDeleteAPIView(BaseAdminObjectAPIView):
    """
    API View returning the data
    to build the Confirm Delete View in the front-end.

    Deletion happens in `AdminObjectAPIView`.
    """

    def get(self, request, *args, **kwargs):
        # ---------------------------------------------
        # ----------- case where object is not found
        # ---------------------------------------------
        if self.obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        can_view = self.model_admin.has_view_permission(request, self.obj)
        can_delete = self.model_admin.has_delete_permission(request, self.obj)

        # ---------------------------------------------
        # ----------- case where no view/delete permission
        # ---------------------------------------------
        if not can_view or not can_delete:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # ---------------------------------------------
        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        (
            deleted_objects,  # [str]
            model_count,  # {"model_name": num of deleting objects}
            perms_needed,  # permissions needed that do not exist
            protected,  # objects that have PROTECTED relation
        ) = get_deleted_objects([self.obj], request, self._admin_site)

        if hasattr(self.model_admin, "get_delete_extra_data"):
            extra_data = self.model_admin.get_delete_extra_data(request, self.obj)
        else:
            extra_data = None

        # ---------------------------------------------
        return Response(
            data={
                "object_repr": str(self.obj),
                "permissions": {
                    "view": can_view,
                    "delete": not protected and not perms_needed,
                },
                "deleted_objects": deleted_objects,
                "model_count": {str(m): str(model_count[m]) for m in model_count},
                "perms_needed": tuple(perms_needed),
                "protected": tuple(protected),
                #
                "extra_data": extra_data,
            },
            status=status.HTTP_200_OK,
        )
