from . import views as api_views
from .views import autocomplete

VIEWMAP = {
    # ------------------------------------------------
    # auth
    # ------------------------------------------------
    "password_change": (
        "password_change/",
        api_views.PasswordChange,
        None,
    ),
    "token_obtain_pair": (
        "token/",
        api_views.AdminTokenObtainPairView,
        None,
    ),
    "token_refresh": (
        "token/refresh/",
        api_views.AdminTokenRefreshView,
        None,
    ),
    # ------------------------------------------------
    # autocomplete
    # ------------------------------------------------
    "filter_autocomplete": (
        "filter_autocomplete/<str:app_name>/<str:model_name>/",
        autocomplete.AutocompleteFilterAPIView,
        None,
    ),
    "filter_autocomplete_retrieve_label": (
        "filter_autocomplete/<str:app_name>/<str:model_name>/<str:pk>/",
        autocomplete.AutocompleteFilterRetrieveLabelAPIView,
        None,
    ),
    "field_autocomplete": (
        "field_autocomplete/",
        autocomplete.FieldAutocompleteAPIView,
        None,
    ),
    # ------------------------------------------------
    # base info
    # ------------------------------------------------
    "base_info": (
        "base_info/",
        api_views.AdminBaseInfoAPIView,
        None,
    ),
    # ------------------------------------------------
    # list
    # ------------------------------------------------
    "admin_list_create": (
        "<str:app_name>/<str:model_name>/",
        api_views.AdminListCreateAPIView,
        None,
    ),
    "admin_list_info": (
        "<str:app_name>/<str:model_name>/info/",
        api_views.AdminListInfoAPIView,
        None,
    ),
    "admin_list_action_preview": (
        "<str:app_name>/<str:model_name>/action/<str:action_name>/preview/",
        api_views.AdminListActionPreviewAPIView,
        None,
    ),
    "admin_list_action_execute": (
        "<str:app_name>/<str:model_name>/action/<str:action_name>/execute/",
        api_views.AdminListActionExecuteAPIView,
        None,
    ),
    # ------------------------------------------------
    # object
    # ------------------------------------------------
    "admin_object_view": (
        "<str:app_name>/<str:model_name>/<str:pk>/view/",
        api_views.AdminObjectViewAPIView,
        None,
    ),
    "admin_object_add": (
        "<str:app_name>/<str:model_name>/add/",
        api_views.AdminObjectAddAPIView,
        None,
    ),
    "admin_object_edit": (
        "<str:app_name>/<str:model_name>/<str:pk>/edit/",
        api_views.AdminObjectEditAPIView,
        None,
    ),
    "admin_object_delete_confirm": (
        "<str:app_name>/<str:model_name>/<str:pk>/delete/",
        api_views.AdminObjectConfirmDeleteAPIView,
        None,
    ),
    "admin_object_history": (
        "<str:app_name>/<str:model_name>/<str:pk>/history/",
        api_views.AdminHistoryAPIView,
        None,
    ),
    # retrieve with minimum info (GET),
    # update (PUT),
    # delete (DELETE)
    "admin_object": (
        "<str:app_name>/<str:model_name>/<str:pk>/",
        api_views.AdminObjectAPIView,
        None,
    ),
}
