import copy

from typing import Any

from django.contrib import admin
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest
from django.utils.html import format_html, mark_safe
from django.urls import reverse


from admin.django_admin.filters.real_estate import (
    property_admin_list_filters,
    agreement_admin_list_filters,
)
from backend.real_estate.models import (
    # Project
    Project,
    RelatedProject,
    ProjectAddress,
    ProjectDocument,
    ProjectFile,
    ProjectImage,
    ProjectContact,
    # Property
    PropertyType,
    Property,
    PropertyAssociatedContact,
    PropertyOwner,
    PropertyDocument,
    PropertyFile,
    PropertyImage,
    # Agreement
    Agreement,
    AgreementCommission,
    AgreementRelatedContact,
    AgreementParty,
    AgreementDocument,
)
from backend.real_estate.constants import (
    PROPERTY_CATEGORY_BUILDING_FIELDS_MAPPING,
    PROPERTY_CATEGORY_ENERGY_FIELDS_MAPPING,
    PROPERTY_CATEGORY_EXTRAS_FIELDS_MAPPING,
)

from ..forms import real_estate as real_estate_forms

# % --------------  Project  -----------------


class RelatedProjectInline(admin.TabularInline):
    model = RelatedProject
    fk_name = "related_project"
    autocomplete_fields = ("project",)
    verbose_name = "Related Project"
    extra = 0


class ProjectAddressInline(admin.TabularInline):
    model = ProjectAddress
    autocomplete_fields = ("address",)
    verbose_name = "Address"
    verbose_name_plural = "Addresses"
    extra = 0


class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    verbose_name = "Document"
    extra = 0


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    verbose_name = "File"
    extra = 0


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    verbose_name = "Image"
    fields = ("project", "image", "notes")
    extra = 0


class ProjectContactInline(admin.TabularInline):
    model = ProjectContact
    autocomplete_fields = ("contact",)
    verbose_name = "Contact"
    extra = 0


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "type",
        "construction_stage",
        "start_date",
        "developer",
    )
    fields = (
        "created_at",
        "name",
        "type",
        "construction_stage",
        "developer",
        "energy_efficiency_grade",
        "website_url",
        "number_of_units",
        "location_description",
        "amentities_description",
        "start_date",
        "completion_date",
        "starting_price_from",
        "address",
        "expected_completion_date",
    )
    readonly_fields = ("created_at",)
    list_select_related = ("developer",)
    search_fields = (
        "name",
        "developer__contact__first_name",
        "developer__contact__email__address",
        "developer__contact__last_name",
        "developer__contact__name",
        "developer__user__email",
        "developer__user__first_name",
        "developer__user__last_name",
    )
    autocomplete_fields = ("developer", "address")
    inlines = (
        RelatedProjectInline,
        ProjectAddressInline,
        ProjectDocumentInline,
        ProjectFileInline,
        ProjectImageInline,
        ProjectContactInline,
    )


# % --------------  Property Category/Type  -----------------


class PropertyTypeAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_filter = ("category",)


# % --------------  Property  -----------------


class PropertyAssociatedContactInline(admin.TabularInline):
    model = PropertyAssociatedContact
    autocomplete_fields = ("contact",)
    verbose_name = "Associated Contact"
    extra = 0


class PropertyOwnerInline(admin.TabularInline):
    model = PropertyOwner
    autocomplete_fields = ("owner",)
    verbose_name = "Owner"
    formset = real_estate_forms.PropertyOwnerFormSet
    extra = 0


class PropertyAgreementInline(admin.StackedInline):
    model = Agreement
    fields = (
        "type",
        "created_at",
        "updated_at",
        "status",
        "agreement_signing_date",
        "valid_from",
        "valid_until",
        "cancel_date",
        "assigned_to",
        "link_to_agreement",
    )
    readonly_fields = ("created_at", "updated_at", "link_to_agreement")

    def link_to_agreement(self, obj=None):
        href = reverse("admin:real_estate_agreement_change", kwargs={"object_id": obj.id})
        return mark_safe(
            f'<a href="{href}" target="_blank">'
            '<i class="fas fa-square-arrow-up-right" style="font-size: 25px !important;"></i></a>'
        )

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PropertyDocumentInline(admin.TabularInline):
    model = PropertyDocument
    verbose_name = "Document"


class PropertyFileInline(admin.TabularInline):
    model = PropertyFile
    verbose_name = "File"


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    verbose_name = "Image"
    fields = ("property", "image", "notes")


class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "type",
        "utilization",
        "status",
        "unit_number",
        "assigned_to",
    )
    list_filter = property_admin_list_filters
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "project__name",
    )
    inlines = (
        PropertyAgreementInline,
        PropertyOwnerInline,
        PropertyAssociatedContactInline,
        PropertyDocumentInline,
        PropertyFileInline,
        PropertyImageInline,
    )
    autocomplete_fields = (
        "assigned_to",
        "project",
        "address",
    )

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        if obj is None:
            return (
                (
                    "Basic info",
                    {
                        "fields": (
                            "name",
                            "type",
                            "status",
                            "utilization",
                            "short_description",
                            "description",
                            "project",
                            "unit_number",
                            "assigned_to",
                            "address",
                        )
                    },
                ),
            )

        category_slug = obj.type.category.slug

        fieldsets = [
            (
                "General",
                {
                    "fields": (
                        "created_at",
                        "updated_at",
                        "name",
                        "type",
                        "utilization",
                        "status",
                        "short_description",
                        "description",
                        "project",
                        "unit_number",
                        "address",
                        "assigned_to",
                        "list_selling_price",
                        "list_rental_price",
                    )
                },
            ),
            (
                "Energy",
                {"fields": PROPERTY_CATEGORY_ENERGY_FIELDS_MAPPING[category_slug]},
            ),
            (
                "Visuals",
                {
                    "fields": (
                        "inherit_project_media",
                        "image",
                    )
                },
            ),
            (
                "Distances",
                {
                    "fields": (
                        "distance_from_school",
                        "distance_from_airport",
                        "distance_from_university",
                        "distance_from_beach",
                        "distance_from_hospital",
                        "distance_from_shops",
                        "distance_from_tube_station",
                        "distance_from_rail_station",
                        "distance_from_center",
                    )
                },
            ),
            (
                "Extras",
                {"fields": PROPERTY_CATEGORY_EXTRAS_FIELDS_MAPPING[category_slug]},
            ),
        ]

        if category_slug != "land":
            fieldsets.insert(
                1,
                (
                    "Building",
                    {"fields": PROPERTY_CATEGORY_BUILDING_FIELDS_MAPPING[category_slug]},
                ),
            )

        return fieldsets

    def get_readonly_fields(self, request: HttpRequest, obj: Any | None = ...):
        if obj is None:
            return ()
        else:
            return (
                "type",
                "created_at",
                "updated_at",
            ) + super().get_readonly_fields(request, obj)


# % --------------  Agreement  -----------------


class AgreementRelatedContactInline(admin.TabularInline):
    model = AgreementRelatedContact
    autocomplete_fields = ("contact",)
    verbose_name = "Related Contact"
    extra = 0


class AgreementCommissionInline(admin.TabularInline):
    model = AgreementCommission
    autocomplete_fields = ("beneficiary",)
    verbose_name = "Commission party"
    verbose_name_plural = "Commission parties"
    extra = 0
    max_num = 1

    # def has_delete_permission(self, request, obj=None):
    #     return True

    # def has_change_permission(self, request, obj=None):
    #     return False

    # def has_view_permission(self, request, obj=None):
    #     return False


class AgreementDocumentInline(admin.TabularInline):
    model = AgreementDocument
    verbose_name = "Document"
    fields = (
        "file",
        "identifier",
        "type",
        "issuer",
        "issued_at",
        "valid_from",
        "valid_until",
        "notes",
    )
    extra = 0


class AgreementAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "type",
        "id",
        "created_at",
        "updated_at",
        "reservation_date",
        "assigned_to",
        "project",
        "property",
        "assigned_to",
        "valid_from",
        "valid_until",
        "cancel_date",
    )
    list_select_related = (
        "project",
        "property",
    )
    search_help_text = format_html(
        "Search for Agreement ID, Lead name, <br>Lead contacts' name/first last name <br>or project's/property's name"
    )
    fields = (
        # General
        "created_at",
        "updated_at",
        "type",
        "status",
        "agreement_signing_date",
        "signing_time",
        "assigned_to",
        "project",
        "property",
        "unique_id",
        "website_url",
        "slug",
        "closure_percentage",
        "agreement_int",
        "description",
        "valid_from",
        "valid_until",
        "cancel_date",
        "reservation_date",
        "price",
        "down_payment",
        # Details
        "private_agreement_date",
    )
    autocomplete_fields = (
        "project",
        "property",
        "assigned_to",
    )
    search_fields = (
        "id",
        "project__name",
        "property__name",
    )
    list_filter = agreement_admin_list_filters
    inlines = (
        AgreementCommissionInline,
        AgreementDocumentInline,
        AgreementRelatedContactInline,
    )

    enable_comments = True
    owner_field_name = "assigned_to"
    export_fields_exclude = ("comments",)

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if obj is None:
            return ("created_at", "updated_at")
        else:
            return ("type", "created_at", "updated_at")


admin.site.register(Project, ProjectAdmin)
admin.site.register(PropertyType, PropertyTypeAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Agreement, AgreementAdmin)
