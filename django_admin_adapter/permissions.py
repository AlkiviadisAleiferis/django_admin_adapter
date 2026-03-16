from rest_framework.permissions import BasePermission


class AdminSiteBasePermission(BasePermission):
    """
    Delegate basic permission handling to adapter's
    `AdminSite.has_pemission`.
    """

    def has_permission(self, request, view):
        return view._admin_site.has_permission(request)
