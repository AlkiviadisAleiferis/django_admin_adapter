from django.contrib import admin
from django.utils.html import format_html

from backend.archive.models import (
    File,
    Image,
    Document,
    DocumentFile,
    DocumentImage,
)


class FileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "uploader",
        "created_at",
        "updated_at",
    )
    fields = (
        "file",
        "name",
        "description",
        "uploader",
        "created_at",
        "updated_at",
        "file_path",
    )
    search_fields = ("name",)
    readonly_fields = (
        "uploader",
        "created_at",
        "updated_at",
        "file_path",
    )

    owner_field_name = "uploader"

    def file_path(self, obj=None):
        if obj is None:
            return "-"
        return obj.file.path


class ImageAdmin(admin.ModelAdmin):
    list_display = (
        "image_tag",
        "name",
        "file_path",
        "uploader",
        "created_at",
        "updated_at",
    )
    fields = (
        "img",
        "name",
        "description",
        "file_path",
        "uploader",
        "created_at",
        "updated_at",
        "image_preview",
    )
    search_fields = ("name", "content_type")
    readonly_fields = (
        "file_path",
        "uploader",
        "created_at",
        "updated_at",
        "image_preview",
    )

    owner_field_name = "uploader"

    def file_path(self, obj=None):
        if obj is None:
            return "-"
        return obj.img.path

    def image_preview(self, obj=None):
        if obj is None:
            return "-"
        return format_html(
            '<img src="{}" class="elevation-2" style="max-width:700px; max-height:700px"/>'.format(
                obj.img.url
            )
        )

    def image_tag(self, obj):
        return format_html(
            '<img src="{}" style="max-width:150px; max-height:150px"/>'.format(
                obj.img.url
            )
        )

    image_tag.short_description = "preview"


class DocumentFileInline(admin.TabularInline):
    model = DocumentFile
    verbose_name_plural = "Files"
    fields = ("document", "file", "name", "notes")


class DocumentImageInline(admin.TabularInline):
    model = DocumentImage
    verbose_name_plural = "Images"
    image_field_name = "img"
    fields = ("document", "img", "name", "notes")


class DocumentAdmin(admin.ModelAdmin):
    owner_field_name = "uploader"

    list_display = (
        "identifier",
        "document_type",
        "created_at",
        "updated_at",
        "uploader",
        "issuer",
        "issued_at",
        "expires_at",
    )
    list_select_related = ("document_type",)
    fields = (
        "document_type",
        "identifier",
        "uploader",
        "issuer",
        "issued_at",
        "expires_at",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "uploader",
        "created_at",
        "updated_at",
    )
    list_filter = ("document_type",)
    search_fields = ("identifier", "files__name", "images__name")
    inlines = (
        DocumentFileInline,
        DocumentImageInline,
    )


admin.site.register(File, FileAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Document, DocumentAdmin)
