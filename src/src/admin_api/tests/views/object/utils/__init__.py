from .view import get_object_view_data
from .add import get_object_add_data
from .edit import get_object_edit_data
from .delete import get_object_delete_data
from .object_history import get_object_history_data
from .update import get_update_agreement_response
from .common import DummyRequest


__all__ = [
    "get_object_view_data",
    "get_object_add_data",
    "get_object_edit_data",
    "get_object_delete_data",
    "get_object_history_data",
    "get_update_agreement_response",
]
