import inspect

from copy import deepcopy
from django.apps import apps
from django.contrib.admin.sites import AdminSite, DefaultAdminSite
from django.urls import path
from django.urls.resolvers import URLPattern
from rest_framework import authentication
from rest_framework.throttling import BaseThrottle
from rest_framework.views import APIView
from typing import Tuple, List, Mapping

from .viewmap import VIEWMAP
from .throttling import AdminAnonRateThrottle, AdminUserRateThrottle
from .exceptions import AdminAPIAdapterError
from .permissions import AdminSiteBasePermission
from .serializers import (
    AdminHistorySerializer,
    AdminListSerializer,
    AdminObjectViewSerializer,
    CustomTokenObtainPairSerializer,
)


extra_views_type = Mapping[str, Tuple[str, type[APIView], List[type[BaseThrottle]]|None]] | None



class AdminAPIAdapter:
    default_anon_throttle_class: type[BaseThrottle] = AdminAnonRateThrottle
    default_user_throttle_class: type[BaseThrottle] = AdminUserRateThrottle
    authentication_throttle_class = None

    authentication_views_names = ("token_obtain_pair", "token_refresh")
    authentication_class: type[authentication.BaseAuthentication] | None = None

    base_permission_class = AdminSiteBasePermission

    object_serializer_class = AdminObjectViewSerializer
    list_serializer_class = AdminListSerializer
    history_serializer_class = AdminHistorySerializer
    token_obtain_pair_serializer = CustomTokenObtainPairSerializer

    history_page_size: int = 30
    autocomplete_max_objects: int = 10

    def __init__(
        self,
        admin_site: AdminSite|DefaultAdminSite,
        sidebar_registry: List[dict]|None = None,
        extra_views: extra_views_type = None,
        default_anon_throttle_class: type[BaseThrottle] | None = None,
        default_user_throttle_class: type[BaseThrottle] | None = None,
        authentication_throttle_class: type[BaseThrottle] | None = None,
        authentication_class: type[authentication.BaseAuthentication] | None = None,
        **kwargs
    ) -> None:
        """
        PARAMETERS:
            `admin_site`: Is the admin site to be registered \
                and expose its endpoints

            `sidebar_registry`: [
                {
                    "type": "dropdown" | "model" | "view", # required
                    "icon": str, # NOT required
                    "label": str, # required

                    "view_name": str, # required --> for "view" type only
                    "client_view_path": str, # required --> for "view" type only

                    "app_name": Model._meta.app_label, # required --> for "model" type only
                    "model_name": Model._meta.model_name, # required --> for "model" type only

                    "dropdown_entries": [ # --> only in case of "dropdown" type
                        {
                            "type": "model" | "view",
                            "label": str,
                            "icon": str,
                            "app_name": Model._meta.app_label,
                            "model_name": Model._meta.model_name,
                            "view_name": str,
                        }
                    ]
                }, ..
            ]

            `extra_views`: {
                "view_name": (
                    "path/to/view/",
                    `APIView`,
                    throttle_classes_list,
                ), ..
            }

            `default_anon_throttle_class`: default Anon throttle class
            `default_user_throttle_class`: default user authenticated throttle class
            `authentication_throttle_class`: throttle class for authentication views

            `authentication_class`: authentication.BaseAuthentication
        """
        if authentication_class is None:
            try:
                from rest_framework_simplejwt.authentication import JWTAuthentication
                self.authentication_class = JWTAuthentication
            except ImportError:
                raise AdminAPIAdapterError(
                    "`authentication_class` is not provided and "
                    "`rest_framework_simplejwt` is not installed."
                )
            # TODO: check `rest_framework_simplejwt` version compatibility


        if not isinstance(admin_site, (AdminSite, DefaultAdminSite)):
            raise AdminAPIAdapterError(
                "`admin_site` provided is not a subclass of `django.contrib.admin.sites.AdminSite`"
            )
        self.admin_site = admin_site


        extra_views = extra_views or {}
        self.validate_extra_views(extra_views)

        self.views_mapping = deepcopy(VIEWMAP)
        self.views_mapping.update(extra_views)

        self.setup_sidebar_registry(sidebar_registry)

        # ------- throttle classes -------

        self.setup_throttle_classes(
            default_anon_throttle_class,
            default_user_throttle_class,
            authentication_throttle_class,
        )
        self.setup_authentication_class(authentication_class)

        # ------- set all kwargs as instance attrs -------
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def validate_extra_views(self, extra_views: dict) -> None:
        if not isinstance(extra_views, dict):
            raise AdminAPIAdapterError("extra_views must be of type dict.")

        for view_name, view_data in extra_views.items():
            if len(view_data) != 3:
                raise AdminAPIAdapterError(
                    f"Data provided for '{view_name}' must be in "
                    "('view_path', ViewClass, [ThrottleClass, ThrottleClass]) format"
                )
            if not isinstance(view_data[0], str):
                raise AdminAPIAdapterError(
                    f"view path for '{view_name}' must be of type str."
                )
            if not issubclass(view_data[1], APIView):
                raise AdminAPIAdapterError(
                    f"ViewClass for '{view_name}' must be a subclass of rest_framework.views.APIView."
                )
            if view_data[2] is not None:
                if not isinstance(view_data[2], (list, tuple)):
                    raise AdminAPIAdapterError(
                        f"Throttle classes for '{view_name}' must be of type list or tuple."
                    )
                if len(view_data[2]) != 2:
                    raise AdminAPIAdapterError(
                        f"Throttle classes for '{view_name}' must be of length 2."
                    )
                for throttle_class in view_data[2]:
                    if not issubclass(throttle_class, BaseThrottle):
                        raise AdminAPIAdapterError(
                            f"Throttle class '{throttle_class}' for '{view_name}' must be a subclass of rest_framework.throttling.BaseThrottle."
                        )

    def validate_sidebar_entry(self, entry: dict, is_dropdown: bool=False):
        if not isinstance(entry, dict):
            raise AdminAPIAdapterError(
                "sidebar_registry entries must be of type dict."
            )

        type_ = entry.get("type")
        label = entry.get("label")
        icon = entry.get("icon")

        if type_ is None:
            raise AdminAPIAdapterError(
                "sidebar_registry entry type missing."
            )
        elif type_ not in ("dropdown", "model", "view"):
            raise AdminAPIAdapterError(
                f"sidebar_registry entry invalid type: '{type_}'."
            )
        elif label is None:
            raise AdminAPIAdapterError(
                "sidebar_registry entry label missing."
            )
        elif not isinstance(label, str):
            raise AdminAPIAdapterError(
                "sidebar_registry entry label must be of type str."
            )
        elif icon and not isinstance(icon, str):
            raise AdminAPIAdapterError(
                "sidebar_registry entry icon must be of type str."
            )
        elif is_dropdown and type_ == "dropdown":
            raise AdminAPIAdapterError(
                "sidebar_registry dropdown does not support "
                "nested dropdowns."
            )

        # --------------------
        # validate view entry

        if type_ == "view":
            view_name = entry.get("view_name")
            client_view_path = entry.get("client_view_path")

            if view_name is None:
                raise AdminAPIAdapterError(
                    "sidebar_registry view entry view_name missing."
                )
            elif not isinstance(view_name, str):
                raise AdminAPIAdapterError(
                    "sidebar_registry view entry view_name must be of type str."
                )
            elif view_name not in self.views_mapping:
                raise AdminAPIAdapterError(
                    "sidebar_registry view entry view_name "
                    f"'{view_name}' not in provided views."
                )
            elif not client_view_path:
                raise AdminAPIAdapterError(
                    f"sidebar_registry view entry '{view_name}' client_view_path missing."
                )
            elif not isinstance(client_view_path, str):
                raise AdminAPIAdapterError(
                    f"sidebar_registry view entry '{view_name}' client_view_path must be of type str."
                )

            entry["client_view_path"] = client_view_path
            entry["view_class"] = self.views_mapping[view_name][1]

        # --------------------
        # validate model entry

        elif type_ == "model":
            app_name = entry.get("app_name")
            model_name = entry.get("model_name")

            if app_name is None:
                raise AdminAPIAdapterError(
                    "sidebar_registry model entry's app_name missing."
                )
            elif not isinstance(app_name, str):
                raise AdminAPIAdapterError(
                    "sidebar_registry model entry's "
                    "app_name must be of type str."
                )
            elif model_name is None:
                raise AdminAPIAdapterError(
                    "sidebar_registry model entry's model_name missing."
                )
            elif not isinstance(model_name, str):
                raise AdminAPIAdapterError(
                    "sidebar_registry model entry's "
                    "model_name must be of type str."
                )

            try:
                model = apps.get_model(f"{app_name}.{model_name}")
            except LookupError:
                raise AdminAPIAdapterError(
                    f"Non existing '{app_name}.{model_name}' model entry."
                )

            model_admin = self.admin_site._registry.get(model)

            if model_admin is None:
                raise AdminAPIAdapterError(
                    f"Non existing '{app_name}.{model_name}' "
                    "model admin for model entry."
                )

            entry["model_admin"] = model_admin
            entry["model"] = model
            entry["label"] = model._meta.verbose_name_plural.capitalize()

        # -----------------------
        # validate dropdown entry

        elif type_ == "dropdown":
            if "dropdown_entries" not in entry:
                raise AdminAPIAdapterError("sidebar_registry model entry's dropdown_entries missing.")

            if not isinstance(entry["dropdown_entries"], list):
                raise AdminAPIAdapterError(
                    "sidebar_registry dropdown entry's dropdown_entries "
                    "must be of type list."
                )

            for e in entry["dropdown_entries"]:
                self.validate_sidebar_entry(e, is_dropdown=True)

    def setup_sidebar_registry(self, sidebar_registry: list|None) -> None:
        if sidebar_registry is None:
            self.sidebar_registry = []
            return

        elif not isinstance(sidebar_registry, list):
            raise AdminAPIAdapterError("sidebar_registry must be of type list.")

        for entry in sidebar_registry:
            self.validate_sidebar_entry(entry)

        self.sidebar_registry = sidebar_registry

    def setup_throttle_classes(
        self,
        default_anon_throttle_class,
        default_user_throttle_class,
        authentication_throttle_class,
    ) -> None:
        if default_anon_throttle_class is not None:
            if not inspect.isclass(default_anon_throttle_class):
                raise AdminAPIAdapterError("The `default_anon_throttle_class` provided is not a class.")
            elif not issubclass(default_anon_throttle_class, BaseThrottle):
                raise AdminAPIAdapterError("The `default_anon_throttle_class` provided is not of type `BaseThrottle`.")

            self.default_anon_throttle_class = default_anon_throttle_class

        if default_user_throttle_class is not None:
            if not inspect.isclass(default_user_throttle_class):
                raise AdminAPIAdapterError("The `default_user_throttle_class` provided is not a class.")
            elif not issubclass(default_user_throttle_class, BaseThrottle):
                raise AdminAPIAdapterError("The `default_user_throttle_class` provided is not of type `BaseThrottle`.")

            self.default_user_throttle_class = default_user_throttle_class

        if authentication_throttle_class is None:
            return

        if not inspect.isclass(authentication_throttle_class):
            raise AdminAPIAdapterError("The `authentication_throttle_class` provided is not a class.")
        elif not issubclass(authentication_throttle_class, BaseThrottle):
            raise AdminAPIAdapterError("The `authentication_throttle_class` provided is not of type `BaseThrottle`.")

        self.authentication_throttle_class = authentication_throttle_class

    def setup_authentication_class(self, authentication_class) -> None:
        if authentication_class is None:
            return

        if not inspect.isclass(authentication_class):
            raise AdminAPIAdapterError("The `authentication_class` provided is not a class.")
        elif not issubclass(authentication_class, authentication.BaseAuthentication):
            raise AdminAPIAdapterError(
                "The `authentication_class` provided is not a subclass of "
                "`rest_framework.authentication.BaseAuthentication`."
            )

        self.authentication_class = authentication_class

    def build_view_path(self, view_name) -> URLPattern:
        view_url, ViewClass, throttle_classes_list = self.views_mapping[view_name]

        if view_name not in self.authentication_views_names:
            if throttle_classes_list is None:
                throttle_classes_list = [
                    self.default_anon_throttle_class,
                    self.default_user_throttle_class,
                ]
        elif self.authentication_throttle_class is not None:
            throttle_classes_list = [
                self.authentication_throttle_class,
            ]
        else:
            throttle_classes_list = []

        # subclassing avoids name clashing
        class AdminAdapterAPIView(ViewClass):
            __name__ = ViewClass.__name__
            throttle_classes = throttle_classes_list
            _admin_site = self.admin_site
            _adapter_instance = self
            _admin_view_name = view_name

        if view_name == "token_obtain_pair":
            AdminAdapterAPIView.serializer_class = self.token_obtain_pair_serializer

        # add default authentication
        # and permission classes
        # to every non-authentication view
        if view_name not in self.authentication_views_names:
            AdminAdapterAPIView.authentication_classes = [self.authentication_class]

            if AdminAdapterAPIView.permission_classes:
                permission_classes = [self.base_permission_class] + [
                    p for p in AdminAdapterAPIView.permission_classes
                ]
            else:
                permission_classes = [self.base_permission_class]

            AdminAdapterAPIView.permission_classes = permission_classes


        return path(view_url, AdminAdapterAPIView.as_view(), name=view_name)

    def get_urls(self) -> List[URLPattern]:
        return [self.build_view_path(view_name) for view_name in self.views_mapping]

    def get_extra_base_info_data(self, request):
        return None
