from django.contrib.admin.exceptions import (
    DisallowedModelAdminLookup,
    DisallowedModelAdminToField,
)
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.views.main import ORDER_VAR
from django.contrib.admin.utils import flatten_fieldsets
from django.core.exceptions import SuspiciousOperation, ImproperlyConfigured
from django.db import transaction
from django.forms.formsets import all_valid
from rest_framework.response import Response
from rest_framework import status
from ..utils import get_list_filter_data
from .base import BaseAdminAPIView
from .utils import build_object_error_response


# % ---------------- Change List API Views ----------------


class AdminListCreateAPIView(BaseAdminAPIView):
    def post(self, request, *args, **kwargs):
        if not self.model_admin.has_add_permission(request):
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():
            fieldsets = self.model_admin.get_fieldsets(request, None)
            fieldnames = flatten_fieldsets(fieldsets)
            ModelForm = self.model_admin.get_form(
                request, None, change=False, fields=fieldnames
            )
            form = ModelForm(request.POST, request.FILES)
            formsets, inline_instances = self.model_admin._create_formsets(
                request, form.instance, change=False
            )

            form_validated = form.is_valid()

            if form_validated:
                new_object = self.model_admin.save_form(request, form, change=False)
            else:
                new_object = form.instance

            if all_valid(formsets) and form_validated:
                self.model_admin.save_model(request, new_object, form, False)
                self.model_admin.save_related(request, form, formsets, False)

                change_message = self.model_admin.construct_change_message(
                    request, form, formsets, True
                )
                self.model_admin.log_addition(request, new_object, change_message)

                return Response(
                    data={
                        "messages": [f"New object {new_object} created successfully."],
                        "object": {"pk": new_object.pk, "str": str(new_object)},
                    },
                    status=status.HTTP_201_CREATED,
                )

            else:
                return build_object_error_response(form, formsets)

    def get(self, request, *args, **kwargs):
        can_view = self.model_admin.has_view_or_change_permission(request, None)

        if not can_view:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            changelist = self.model_admin.get_changelist_instance(request)
            # here any query parameters in the request are used
            # to filter down the queryset
            changelist.get_results(request)
        except (
            IncorrectLookupParameters,
            DisallowedModelAdminLookup,
            DisallowedModelAdminToField,
            SuspiciousOperation,
        ):
            return Response(
                data={"messages": ["Incorrect GET parameters."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # validate if page number is out of range
        if changelist.page_num > changelist.paginator.num_pages:
            return Response(
                data={"messages": ["Page number out of range."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # validate if non prohibited sorting is requested
        sortable_by = set(self.model_admin.get_sortable_by(request) or ())
        list_display_dict = {
            index + 1: fieldname
            for index, fieldname in enumerate(
                self.model_admin.get_list_display(request)
            )
        }
        if not self.validate_ordering(request, sortable_by, list_display_dict):
            return Response(
                data={"messages": ["Invalid sorting field(s)."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results_data = self._adapter_instance.list_serializer_class(
            changelist.result_list,
            model_class=self.model,
            all_fields=self.model_admin.get_list_display(request),
            context={"model_admin": self.model_admin},
            many=True,
        ).data

        return Response(
            data={
                "results": results_data,
                "page": changelist.page_num,
                "total_pages": changelist.paginator.num_pages,
                "total_objects_num": changelist.paginator.count,
            },
            status=status.HTTP_200_OK,
        )

    def validate_ordering(self, request, sortable_by, list_display_dict):
        """
        Validate if any of the sorting fields
        are not sortable included in `sortable_by`
        of the `ModelAdmin`.
        """
        if ORDER_VAR in request.GET:
            sorting_fieldnums = request.GET[ORDER_VAR]
            sorting_fieldnums = sorting_fieldnums.replace("-", "")

            for field_num in sorting_fieldnums.split("."):
                if not field_num:
                    continue
                elif not field_num.isdigit():
                    continue
                elif list_display_dict.get(int(field_num)) not in sortable_by:
                    return False

        return True

class AdminListInfoAPIView(BaseAdminAPIView):
    """
    API View returning the:
        - list actions
        - list filters
        - list extra data
    of the `django.contrib.admin.ModelAdmin` class
    """
    def get(self, request, *args, **kwargs):
        can_view = self.model_admin.has_view_or_change_permission(request, None)
        if not can_view:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            changelist = self.model_admin.get_changelist_instance(request)
        except IncorrectLookupParameters:
            return Response(
                data={"message": "Incorrect parameters used in URL."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (
            DisallowedModelAdminLookup,
            DisallowedModelAdminToField,
            SuspiciousOperation,
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # ---------------------------------------
        # thing that matters with filters
        # is recreating the UI in front end
        # that will place properly the query parameters
        # in request URL
        # ---------------------------------------
        (
            filter_specs,
            *_,
            # has_filters,
            # remaining_lookup_params,
            # filters_may_have_duplicates,
            # has_active_filters,
        ) = changelist.get_filters(request)

        filter_data = []

        for spec in filter_specs:
            filter_data.append(get_list_filter_data(changelist, spec))

        action_data = self.model_admin.get_action_choices(request)


        if hasattr(self.model_admin, "get_list_extra_data"):
            # WARNING: list_extra_data must be serializable
            list_extra_data = self.model_admin.get_list_extra_data(request)
        else:
            list_extra_data = None

        return Response(
            data={
                "filters": filter_data,
                "actions": action_data,
                "extra_data": list_extra_data,
                "list_max_show_all": self.model_admin.list_max_show_all,
                "sortable_by": self.model_admin.get_sortable_by(request) or (),
            },
            status=status.HTTP_200_OK,
        )
