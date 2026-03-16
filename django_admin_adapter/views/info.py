from rest_framework.generics import GenericAPIView

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rest_framework.response import Response
from rest_framework import status


# % ---------------- Base info ----------------


class AdminBaseInfoAPIView(GenericAPIView):
    permission_classes = [] # will be set inside adapter

    def build_sidebar_entry(self, request, entry):
        if entry["type"] == "model":
            model_admin = entry["model_admin"]

            if (
                not model_admin.has_module_permission(request)
                or not model_admin.has_view_or_change_permission(request, None)
            ):
                return

            return {
                "type": "model",
                "label": entry["label"],
                "icon": entry.get("icon"),
                "app_name": entry["app_name"],
                "model_name": entry["model_name"],
                "permissions": {
                    "view": True,
                    "add": model_admin.has_add_permission(request),
                    "delete": model_admin.has_delete_permission(request, None),
                },
            }

        elif entry["type"] == "view":
            return {
                "type": "view",
                "label": entry["label"],
                "client_view_path": entry["client_view_path"],
                "icon": entry.get("icon"),
                "view_name": entry["view_name"],
            }

    def get_sidebar_data(self, request):
        # use sidebar_registry structure
        sidebar_data = []

        for entry in self._adapter_instance.sidebar_registry:
            if entry["type"] == "dropdown":
                entries = []

                for e in entry["dropdown_entries"]:
                    data = self.build_sidebar_entry(request, e)
                    if data is not None:
                        entries.append(data)

                if entries:
                    sidebar_data.append(
                        {
                            "type": "dropdown",
                            "label": entry["label"],
                            "icon": entry.get("icon"),
                            "dropdown_entries": entries,
                        }
                    )

            else:
                data = self.build_sidebar_entry(request, entry)
                if data is not None:
                    sidebar_data.append(data)

        return sidebar_data

    def get_profile(self, request):
        user_model = request.user.__class__
        user_model_admin = self._admin_site._registry.get(user_model)

        if user_model_admin is None:
            return {
                "user_pk": None,
                "app_name": None,
                "model_name": None,
                "password_change": False,
            }
        else:
            user = user_model_admin.get_object(request, request.user.pk)
            # The object might be restricted
            # by the `get_queryset`,
            # or the `get_object`
            if user is None:
                return {
                    "user_pk": None,
                    "app_name": None,
                    "model_name": None,
                    "password_change": False,
                }

            module_perm = user_model_admin.has_module_permission(request)
            view_perm = module_perm and user_model_admin.has_view_permission(request, user)
            change_perm = module_perm and user_model_admin.has_change_permission(request, user)

            return {
                "user_pk": request.user.pk if view_perm else None,
                "app_name": user_model._meta.app_label if view_perm else None,
                "model_name": user_model._meta.model_name if view_perm else None,
                "password_change": change_perm,
            }

    def get(self, request, *args, **kwargs):
        return Response(
            data={
                "sidebar": self.get_sidebar_data(request),
                "profile": self.get_profile(request),
                "extra": self._adapter_instance.get_extra_base_info_data(request),
            },
            status=status.HTTP_200_OK,
        )
