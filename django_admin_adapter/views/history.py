from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import get_content_type_for_model
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework import status
from .base import BaseAdminObjectAPIView
from ..logging import logger


PAGE_VAR = "p"


class AdminHistoryAPIView(BaseAdminObjectAPIView):
    def get(self, request, *args, **kwargs):
        # % ----------- case where object is not found -----------
        if self.obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        can_view = self.model_admin.has_view_or_change_permission(request, self.obj)

        history_perm_method = getattr(self.model_admin, "has_history_permission", None)
        can_view_history = history_perm_method(request, self.obj) if history_perm_method else True

        if not can_view or not can_view_history:
            return Response(status=status.HTTP_403_FORBIDDEN)

        logs_qs = (
            LogEntry.objects.filter(
                object_id=self.obj.pk,
                content_type=get_content_type_for_model(self.model),
            )
            .select_related()
            .order_by("-action_time")
        )

        paginator = Paginator(logs_qs, self._adapter_instance.history_page_size)
        page_num = request.query_params.get(PAGE_VAR, 1)

        try:
            page_num = int(page_num)
            if page_num not in paginator.page_range:
                page_num = 1
        except ValueError:
            page_num = 1

        page_obj = paginator.page(page_num)

        serializer = self._adapter_instance.history_serializer_class(page_obj.object_list, many=True)

        return Response(
            data={
                "object_repr": str(self.obj),
                "data": {
                    "results": serializer.data,
                    "page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "total_objects_num": paginator.count,
                },
            },
            status=status.HTTP_200_OK,
        )
