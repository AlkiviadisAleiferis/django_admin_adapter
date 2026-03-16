from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest
from django.contrib import admin

from backend.organization.forms import UserChangeForm, UserCreationForm
from backend.organization.models import (
    User,
)


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


class UserAdmin(BaseUserAdmin, admin.ModelAdmin):
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
        "is_active",
        "last_login",
        "notifications",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
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


admin.site.register(User, UserAdmin)
