from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.html import format_html

from backend.organization.forms import UserChangeForm, UserCreationForm
from backend.organization.models import (
    User,
    Organization,
)
from django.contrib.auth.models import Permission


class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        "action_time",
        "user",
        "content_type",
        "object_repr",
        "change_message",
    )
    list_select_related = ("content_type", "user")
    list_filter = ("content_type__model",)
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "content_type__model",
    )


class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "codename")
    search_fields = ("name", "codename")
    list_per_page = 20
    list_max_show_all = 30
    show_full_result_count = True
    actions = ["test_action"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_module_permission(self, request):
        return request.user.is_superuser

    def test_action(self, queryset):
        return {"data": "test"}


# % --------------  User  -----------------


class UserPermissionInline(admin.TabularInline):
    model = User.user_permissions.through
    autocomplete_fields = ("permission",)
    verbose_name = "Permission"


class UserGroupInline(admin.TabularInline):
    model = User.groups.through
    verbose_name = "Group"

    def has_add_permission(self, request: HttpRequest, obj=None):
        return request.user.is_admin_or_management

    def has_delete_permission(self, request: HttpRequest, obj=None):
        return request.user.is_admin_or_management

    def has_view_permission(self, request: HttpRequest, obj=None):
        return True


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    add_form_template = "admin/auth/user/add_form.html"

    list_display = (
        "username",
        "id",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "created_at",
        "updated_at",
    )
    fields = (
        "username",
        "id",
        "created_at",
        "updated_at",
        "email",
        "first_name",
        "last_name",
        "contact",
        "image",
        "preview_image",
        "is_active",
        "last_login",
        "is_client",
        "is_agent",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "preview_image",
        "last_login",
    )
    search_fields = ("email", "username", "first_name", "last_name")
    inlines = (UserGroupInline,)
    autocomplete_fields = ("contact",)
    list_filter = ()

    fieldsets = ()

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "contact",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if obj is None:
            return (
                "id",
                "created_at",
                "updated_at",
                "preview_image",
                "last_login",
            )
        else:
            if request.user.is_superuser:
                return self.readonly_fields

            elif obj is not None and request.user.id == obj.id:
                return self.readonly_fields + (
                    "is_active",
                    "username",
                    "contact",
                    "is_client",
                    "is_agent",
                )

            elif request.user.is_admin_or_management:
                return self.readonly_fields + (
                    "username",
                    "is_client",
                    "is_agent",
                    "contact",
                )

            else:
                return self.fields

    def get_inlines(self, request: HttpRequest, obj=None):
        if request.user.is_superuser:
            return self.inlines + (UserPermissionInline,)
        return super().get_inlines(request, obj)

    def preview_image(self, obj=None):
        if obj is None:
            return "-"
        else:
            return format_html(
                f'<a href="/{obj.image.url}" target="_blank"><img src="/{obj.image.url}" style="height: 450px !important;"></img></a>'
            )


# % --------------  Organization  -----------------


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name",)
    fields = ("name", "slug", "contact")
    search_fields = ("name",)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ("slug",)
        if request.user and request.user.is_superuser:
            return ()
        else:
            return ("name", "slug")


admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(Permission, PermissionAdmin)

admin.site.register(User, UserAdmin)
admin.site.register(Organization, OrganizationAdmin)
