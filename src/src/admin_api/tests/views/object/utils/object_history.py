from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import get_content_type_for_model
from django.core.paginator import Paginator
from admin_api.urls import admin_adapter
from django_admin_adapter.serializers.history import ACTION_DATETIME_FORMAT


def get_object_history_data(obj, page_num=1):
    """
    Get the object history data for an object.
    Replicates what the AdminHistoryAPIView should return.

    ARGS:
        obj: The object instance to generate history data for
        page: The page number (default: 1)
        page_size: Number of items per page (default: 100)

    RETURNS:
        Dictionary containing the object history data
    """

    # Get all log entries for this object
    logs_qs = (
        LogEntry.objects.filter(
            object_id=obj.pk,
            content_type=get_content_type_for_model(obj.__class__),
        )
        .select_related()
        .order_by("-action_time")
    )

    paginator = Paginator(logs_qs, admin_adapter.history_page_size)

    if page_num not in paginator.page_range:
        page_num = 1

    page_obj = paginator.page(page_num)

    # Serialize the log entries
    results = []
    for log in page_obj.object_list:
        results.append(
            {
                "action_time": log.action_time.strftime(ACTION_DATETIME_FORMAT),
                "user": str(log.user),
                "action": log.get_action_flag_display(),
                "description": log.get_change_message(),
            }
        )

    return {
        "object_repr": str(obj),
        "data": {
            "results": results,
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_objects_num": paginator.count,
        },
    }
