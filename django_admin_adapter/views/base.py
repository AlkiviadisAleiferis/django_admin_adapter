from django.apps import apps

from rest_framework.generics import GenericAPIView

from ..exceptions import InvalidURLParamsError


# % ---------------- Base classes ----------------


class BaseAdminAPIView(GenericAPIView):
    """
    Base class for initializang the attributes of the View.

    Sets:
        - self.model (django.db.models.Model)
        - self.model_admin (django.contrib.admin.ModelAdmin)

    Uses the kwargs 'app_name' and 'model_name' of the url.
    """
    permission_classes = [] # will be set inside adapter

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        app_name = self.kwargs.get("app_name")
        model_name = self.kwargs.get("model_name")

        if app_name is None or model_name is None:
            raise InvalidURLParamsError("Missing URL params (1).")

        try:
            model = apps.get_model(f"{app_name}.{model_name}")
        except LookupError:
            raise InvalidURLParamsError(f"Invalid URL params (1).")

        self.model = model

        model_admin = self._admin_site._registry.get(model)
        if model_admin is None:
            raise InvalidURLParamsError(
                f"Invalid URL params (2)."
            )

        self.model_admin = model_admin
        return model_admin


class BaseAdminObjectAPIView(BaseAdminAPIView):
    """
    Extends `BaseAdminAPIView`
    sets self.obj with provided 'pk' url kwarg.
    """

    def initial(self, request, *args, **kwargs):
        model_admin = super().initial(request, *args, **kwargs)

        pk = self.kwargs.get("pk")

        if pk is None:
            raise InvalidURLParamsError("Missing URL params (2).")

        object_pk = int(pk) if pk.isdigit() else pk
        self.obj = model_admin.get_object(request, object_pk)
