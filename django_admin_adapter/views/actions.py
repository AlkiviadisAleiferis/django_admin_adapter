from django.contrib.admin.exceptions import (
    DisallowedModelAdminLookup,
    DisallowedModelAdminToField,
)
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.utils import model_ngettext
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from .base import BaseAdminAPIView
from ..utils import get_deleted_objects


# % ---------------- Change List API Views ----------------


class BaseAdminActionAPIView(BaseAdminAPIView):
    """
    Base APIView for managing the Preview/Execution of actions.

    Gather and clean provided data for each action:
        data = {
            "select_across": 0 | 1,
            "selected_objects": "1,2,3,...",
        }

    Every action must return a Response in any case [Preview, Execute].

    When previewing, data will be returned to
    describe and guide the user before confirming
    with the format below:
    {
        "name": "action_name",
        "description": "Description of the action to be performed."
        --any extra data needed to describe--
    }

    When confirming, the action must actually
    execute the before described action,
    on the provided queryset.
    """
    permission_classes = [] # will be set inside adapter

    def delete_selected(self, request, queryset, confirm=False):
        """
        Default action which deletes the selected objects.
        Copied directly from source code.

        This action first displays a confirmation page which shows all the
        deletable objects, or, if the user has no permission one of the related
        childs (foreignkeys), a "permission denied" message.

        Next, it deletes all selected objects.

        RETURNS:
            {
                "deletable_objects": [str, .., [str, .. []]],
                "model_count": {"model_verbose_name": count},
                "perms_needed": ["permission1", "permission2", ...],
                "protected": [str, .., [str, .. []]],
            }
        """
        # Populate deletable_objects, a data structure
        # of all related objects
        # that will also be deleted.
        (
            deletable_objects,
            model_count,
            perms_needed,
            protected,
        ) = get_deleted_objects(queryset, request, self._admin_site)

        if not confirm:
            return Response(
                data={
                    "name": "Delete selected objects",
                    "description": "Delete selected objects",
                    "deletable_objects": deletable_objects,
                    "model_count": {str(m): str(model_count[m]) for m in model_count},
                    "perms_needed": tuple(perms_needed),
                    "protected": tuple(protected),
                },
                status=status.HTTP_200_OK,
            )

        if protected or perms_needed:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # The user has already confirmed the deletion.
        # Do the deletion and return None
        # to display the change list view again.

        n = queryset.count()
        if not n:
            return Response(
                data={"messages": ["No objects to perform action on."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # protect the atomicity of the DB transaction
        # wouldn't want LogEntries without deleted objects
        with transaction.atomic():
            for obj in queryset:
                obj_display = str(obj)
                self.model_admin.log_deletion(request, obj, obj_display)
            self.model_admin.delete_queryset(request, queryset)

        return Response(
            data={
                "messages": [
                    f"Successfully deleted {n} {model_ngettext(self.model_admin.opts, n).capitalize()}."
                ]
            },
            status=status.HTTP_200_OK,
        )

    def retrieve_queryset(self, request):
        # get action necessary data
        # and clean them
        data = request.data

        if not isinstance(data, dict):
            return Response(
                data={
                    "messages": ["Malformed data provided (1)."],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        select_across = data.get("select_across", 0)
        selected_objects = data.get("selected_objects", [])

        if not isinstance(selected_objects, list):
            return Response(
                data={
                    "messages": ["Malformed data provided (2)."],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            select_across = int(select_across)
        except ValueError:
            return Response(
                data={
                    "messages": ["Malformed data provided (3)."],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not select_across and not selected_objects:
            return Response(
                data={
                    "messages": ["No objects were selected."],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif not select_across and selected_objects:
            for pk in selected_objects:
                if not isinstance(pk, (int, str)):
                    return Response(
                        data={
                            "messages": ["Malformed data provided (4)."],
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        # retrieve the queryset
        try:
            cl = self.model_admin.get_changelist_instance(request)
            queryset = cl.get_queryset(request)
            if not select_across and selected_objects:
                queryset = queryset.filter(pk__in=selected_objects)
            return queryset
        except (
            SuspiciousOperation,
            PermissionDenied,
            DisallowedModelAdminToField,
            IncorrectLookupParameters,
            DisallowedModelAdminLookup,
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request, confirm, *args, **kwargs):
        action_name = self.kwargs["action_name"]
        available_actions = self.model_admin.get_actions(request)

        if action_name not in available_actions:
            return Response(status=status.HTTP_404_NOT_FOUND)

        result = self.retrieve_queryset(request)

        # if result is Response an error occurred
        # return the Response immediately
        if isinstance(result, Response):
            return result
        else:
            queryset = result

        if action_name == "delete_selected":
            return self.delete_selected(request, queryset, confirm=confirm)

        func, _action_name, _description = available_actions[action_name]
        return func(self.model_admin, request, queryset, confirm=confirm)


class AdminListActionPreviewAPIView(BaseAdminActionAPIView):
    def post(self, request, *args, **kwargs):
        return super().post(request, confirm=False, *args, **kwargs)


class AdminListActionExecuteAPIView(BaseAdminActionAPIView):
    def post(self, request, *args, **kwargs):
        return super().post(request, confirm=True, *args, **kwargs)
