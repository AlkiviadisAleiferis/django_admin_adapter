import logging

from rest_framework.generics import GenericAPIView

from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from django.contrib.admin import site as default_admin_site
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist, PermissionDenied

from ..exceptions import InvalidURLParamsError

logger = logging.getLogger()


DEFAULT_RETURN_OBJECTS_NUM = 10


class BaseFilterAutocompleteAPIView(GenericAPIView):
    permission_classes = [] # will be set inside adapter

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        self.request = request

        model_name = self.kwargs.get("model_name")
        if model_name is None:
            raise InvalidURLParamsError("Missing URL params (1).")

        app_name = self.kwargs.get("app_name")
        if app_name is None:
            raise InvalidURLParamsError("Missing URL params (2).")

        try:
            model_class = apps.get_model(f"{app_name}.{model_name}")
        except LookupError:
            raise InvalidURLParamsError("Invalid URL params (3).")

        model_admin = default_admin_site._registry.get(model_class)
        if model_admin is None:
            raise InvalidURLParamsError("Invalid URL params (4).")

        if not model_admin.has_view_or_change_permission(request, obj=None):
            raise PermissionDenied()

        self.model_class = model_class
        self.model_admin = model_admin


class AutocompleteFilterAPIView(BaseFilterAutocompleteAPIView):
    def get(self, request, *args, **kwargs):
        term = request.GET.get("q", "")

        if not term:
            qs = self.model_admin.get_queryset(self.request)
        else:
            qs = self.model_admin.get_queryset(self.request)
            qs, search_use_distinct = self.model_admin.get_search_results(self.request, qs, term)

            if search_use_distinct:
                qs = qs.distinct()

        max_returned_objs = self._adapter_instance.autocomplete_max_objects or DEFAULT_RETURN_OBJECTS_NUM

        return Response(
            data=[
                {
                    "value": obj.pk,
                    "label": str(obj)} for obj in qs[:max_returned_objs]
            ]
        )


class AutocompleteFilterRetrieveLabelAPIView(BaseFilterAutocompleteAPIView):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["pk"]

        obj = self.model_admin.get_object(self.request, object_id)

        if obj is None:
            return Response(data=None)
        else:
            return Response(data={"value": obj.pk, "label": str(obj)})


class FieldAutocompleteAPIView(GenericAPIView):
    permission_classes = [] # will be set inside adapter

    def initial(self, request, *args, **kwargs):
        """
        This method follows the process in
        django.contrib.admin.views.autocomplete.AutocompleteJsonView.process_request

        Validate request integrity, extract and return request parameters.

        Since the subsequent view permission check requires the target model
        admin, which is determined here, raise PermissionDenied if the
        requested app, model or field are malformed.

        Raise ParseError if the target model admin is not configured properly with
        `search_fields`.
        """
        super().initial(request, *args, **kwargs)

        term = request.GET.get("q", "")
        try:
            app_name = request.GET["app_label"]
            model_name = request.GET["model_name"]
            field_name = request.GET["field_name"]
        except KeyError:
            raise InvalidURLParamsError("Missing URL params (1).")

        # Retrieve objects from parameters.
        try:
            source_model = apps.get_model(app_name, model_name)
        except LookupError:
            raise InvalidURLParamsError("Invalid URL params (1).")

        try:
            source_field = source_model._meta.get_field(field_name)
        except FieldDoesNotExist:
            raise InvalidURLParamsError("Invalid URL params (2).")

        try:
            remote_model = source_field.remote_field.model
        except AttributeError:
            raise InvalidURLParamsError("Invalid URL params (3).")

        try:
            remote_model_admin = default_admin_site._registry[remote_model]
        except KeyError:
            raise InvalidURLParamsError("Invalid URL params (4).")

        # Validate suitability of objects.
        if not remote_model_admin.get_search_fields(request):
            raise InvalidURLParamsError("Invalid URL params (5).")

        to_field_name = getattr(
            source_field.remote_field, "field_name", remote_model._meta.pk.attname
        )
        to_field_name = remote_model._meta.get_field(to_field_name).attname

        if not remote_model_admin.has_view_or_change_permission(request):
            raise InvalidURLParamsError()

        if not remote_model_admin.to_field_allowed(request, to_field_name):
            raise InvalidURLParamsError()

        self.term, self.remote_model_admin, self.source_field, self.to_field_name = (
            term,
            remote_model_admin,
            source_field,
            to_field_name,
        )

    def get(self, request, *args, **kwargs):
        qs = self.remote_model_admin.get_queryset(self.request)
        qs = qs.complex_filter(self.source_field.get_limit_choices_to())
        qs, search_use_distinct = self.remote_model_admin.get_search_results(
            self.request, qs, self.term
        )
        if search_use_distinct:
            qs = qs.distinct()

        max_returned_objs = self._adapter_instance.autocomplete_max_objects or DEFAULT_RETURN_OBJECTS_NUM

        return Response(
            data=[
                {"value": str(getattr(obj, self.to_field_name)), "label": str(obj)}
                for obj in qs[:max_returned_objs]
            ]
        )
