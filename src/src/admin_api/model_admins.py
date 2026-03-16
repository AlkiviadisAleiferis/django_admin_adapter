import copy

from typing import Any

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django import forms
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse


from backend.real_estate.models import (
    Project,
    Property,
    Agreement,
    AgreementCommission,
    PropertyAssociatedContact,
    PropertyOwner,
    PropertyDocument,
    PropertyImage,
    PropertyFile,
)
from backend.common.models import (
    Email,
    Contact,
    ContactEmployee,
    ContactImage,
    ContactFile,
    ContactDocument,
    ContactAddress,
    ContactEmail,
    ContactPhone,
)
from backend.real_estate.constants import (
    PROPERTY_CATEGORY_BUILDING_FIELDS_MAPPING,
    PROPERTY_CATEGORY_ENERGY_FIELDS_MAPPING,
    PROPERTY_CATEGORY_EXTRAS_FIELDS_MAPPING,
)
from .filters.real_estate import agreement_admin_list_filters, porperty_list_filters


# ------------ Project ------------


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
    search_fields = ("name",)
    list_per_page = 20


# ------------ Property ------------


class PropertyAssociatedContactInline(admin.TabularInline):
    model = PropertyAssociatedContact
    # autocomplete_fields = ("contact",)
    verbose_name = "Associated Contact"
    # extra = 4
    # min_num = 3
    # max_num = 4


class PropertyOwnerFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        total_ownership = 0

        forms_changed = 0

        # Agreement that can affect owners
        can_change_owners = self.instance.can_change_owners()

        for form in self.forms:
            if not form.cleaned_data.get("DELETE"):
                if form.cleaned_data.get("percentage"):
                    total_ownership += form.cleaned_data["percentage"]
                if form.has_changed():
                    forms_changed += 1

        if forms_changed and not can_change_owners:
            raise ValidationError(
                "Cannot change the owenership of a property with active Sales Agreement."
            )

        if total_ownership != 1 and total_ownership != 0:
            raise ValidationError("The asset's total ownership must be 100%")


class PropertyOwnerInline(admin.TabularInline):
    model = PropertyOwner
    # autocomplete_fields = ("owner",)
    verbose_name = "Owner"
    formset = PropertyOwnerFormSet
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False


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
        return mark_safe(
            f'<a href="/real_estate/agreement/{obj.id}/" target="_blank">'
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
    # readonly_fields = ("notes",)


class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "type",
        "utilization",
        "status",
        "project",
        "unit_number",
        "assigned_to",
        "address",
        "testfield",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "testfield",
    )
    search_fields = (
        "name",
        "project__name",
    )
    list_select_related = (
        "assigned_to",
        "project",
        "address",
    )
    list_filter = ("type", "utilization") + porperty_list_filters
    autocomplete_fields = ("project",)
    inlines = (
        PropertyAssociatedContactInline,
        PropertyOwnerInline,
        PropertyAgreementInline,
        PropertyDocumentInline,
        PropertyFileInline,
        PropertyImageInline,
    )
    list_per_page = 20

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
                        "testfield",
                        "name",
                        "type",
                        "utilization",
                        "status",
                        "short_description",
                        "description",
                        "project",
                        "unit_number",
                        # "address",
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

    def testfield(self, obj):
        return format_html('<p class="bg-danger p-1">' + obj.status + "</p>")

    def get_delete_extra_data(self, request, obj):
        return {"data": "extra data"}


# ------------ Agreement ------------


class AgreementCommissionFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if self.instance.type == Agreement.TypeChoices.CONTRACT_OF_SALE:
            return

        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue

            if form.cleaned_data.get("beneficiary"):
                raise ValidationError(
                    "Only a Contract of Sale Agreement can have beneficiaries."
                )


class AgreementCommissionInline(admin.TabularInline):
    model = AgreementCommission
    extra = 1
    # max_num = 3
    # min_num = 2
    verbose_name = "Commission"
    autocomplete_fields = ("beneficiary",)
    readonly_fields = ("created_at", "updated_at")
    formset = AgreementCommissionFormset

    # def has_add_permission(self, request, obj=None):
    #     return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def has_view_permission(self, request, obj=None):
    #     return False


class AgreementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "type",
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
    list_filter = agreement_admin_list_filters
    list_select_related = (
        "project",
        "property",
        "assigned_to",
    )
    search_help_text = format_html(
        "Search for Agreement ID, Lead name, <br>Lead contacts' name/first last name <br>or project's/property's name"
    )
    fields = (
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
        "private_agreement_date",
    )
    search_fields = (
        "id",
        "project__name",
        "property__name",
    )
    autocomplete_fields = ("property", "project", "assigned_to")
    list_per_page = 20
    show_full_result_count = False
    actions = ["test_action"]
    sortable_by = [
        "created_at",
        "agreement_signing_date",
        "property",
        "valid_from",
        "reservation_date",
        "price",
    ]
    inlines = [AgreementCommissionInline]
    list_max_show_all = 20
    show_full_result_count = False

    def test_action(self, request, queryset, confirm=False):
        from rest_framework.response import Response

        if not confirm:
            return Response(
                data={
                    "name": "Test action",
                    "description": "Test the actions template to see this description",
                },
                status=200,
            )

        return Response(
            data={
                "messages": ["test action executed successfully."],
            },
            status=200,
        )

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if obj is None:
            return ("created_at", "updated_at")
        else:
            return ("type", "created_at", "updated_at")

    def get_list_extra_data(self, request):
        return {"data": "extra data"}

    def get_changeform_initial_data(self, request):
        return {"agreement_int": 1}

    def get_edit_extra_data(self, request, obj):
        return {"data": "extra data"}

    def get_add_extra_data(self, request):
        return {"data": "extra data"}

    def get_view_extra_data(self, request, obj):
        return {"data": "extra data"}

    def get_delete_extra_data(self, request, obj):
        return {"data": "extra data"}


# ------------ Permission ------------


class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "codename")
    search_fields = ("name", "codename")
    list_per_page = 20
    sortable_by = ["name"]
    show_full_result_count = True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_module_permission(self, request):
        return request.user.is_superuser


# ------------ Email ------------


class EmailAdmin(admin.ModelAdmin):
    list_display = ("address",)
    fields = ("address",)
    search_fields = ("address",)

    def has_history_permission(self, request, obj=None):
        return False


# ------------ Contact ------------


class ContactEmailInline(admin.TabularInline):
    model = ContactEmail
    verbose_name = "Email"
    autocomplete_fields = ("email",)


class ContactPhoneInline(admin.TabularInline):
    model = ContactPhone
    verbose_name = "Phone"
    # autocomplete_fields = ("phone",)


class ContactAddressInline(admin.TabularInline):
    model = ContactAddress
    verbose_name = "Address"
    verbose_name_plural = "Addresses"
    # autocomplete_fields = ("country",)


class ContactDocumentInline(admin.TabularInline):
    model = ContactDocument
    verbose_name = "Document"


class ContactFileInline(admin.TabularInline):
    model = ContactFile
    verbose_name = "File"


class ContactImageInline(admin.TabularInline):
    model = ContactImage
    fields = ("contact", "image", "notes")
    verbose_name = "Image"


class ContactEmployeeInline(admin.TabularInline):
    model = ContactEmployee
    fk_name = "employer"
    verbose_name = "Employee"
    autocomplete_fields = ("employee",)


class ContactEmployerInline(admin.TabularInline):
    model = ContactEmployee
    fk_name = "employee"
    verbose_name = "Employer"
    autocomplete_fields = ("employer",)


class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "id",
        "email",
        "phone",
        "nationality",
        "gender",
        "preferred_communication_language",
    )
    list_select_related = (
        "email",
        "phone",
        "nationality",
    )
    search_fields = (
        "name",
        "first_name",
        "last_name",
        "middle_name",
        "id_card_number",
        "passport_number",
        "tax_identification_number",
        "phone__number",
        "email__address",
        "extra_phones__number",
        "extra_emails__address",
    )
    search_help_text = format_html(
        "Search for company name, or first/middle/last name <br>email address or phone number, <br>"
        "Id card number, tax identification number, passport number"
    )
    generic_fields = (
        "created_at",
        "updated_at",
        "type",
        "tax_identification_number",
    )
    # fields common for person/company
    common_fields = (
        "email",
        "phone",
        "notes",
        "preferred_communication_language",
        "preferred_contact_method",
        "country_of_residence",
    )
    consent_fields = (
        "email_consent",
        "phone_consent",
        "sms_consent",
        "marketing_consent",
    )
    company_fields = ("name", "nationality")
    person_fields = (
        "first_name",
        "last_name",
        "middle_name",
        "id_card_number",
        "passport_number",
        "gender",
        "job_title",
        "birth_date",
        "nationality",
    )
    autocomplete_fields = (
        # "country_of_residence",
        # "nationality",
        "email",
        # "phone",
    )
    inlines = (
        ContactEmailInline,
        ContactPhoneInline,
        ContactAddressInline,
        ContactDocumentInline,
        ContactFileInline,
        ContactImageInline,
    )

    dynamic_fields = (
        "type",
        ["name", "first_name", "last_name", "middle_name"],
        {
            Contact.TypeChoices.COMPANY: [
                ["name"],
                ["first_name", "last_name", "middle_name"],
            ],
            Contact.TypeChoices.PERSON: [
                ["first_name", "last_name", "middle_name"],
                ["name"],
            ],
        },
    )

    def get_inlines(self, request, obj=None):
        if obj is None:
            return self.inlines
        else:
            if obj.type == Contact.TypeChoices.COMPANY:
                return (ContactEmployeeInline,) + self.inlines
            else:
                return (ContactEmployerInline,) + self.inlines

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                (
                    "General",
                    {
                        "fields": (
                            "type",
                            "name",
                            "first_name",
                            "last_name",
                            "middle_name",
                            "email",
                            "phone",
                        )
                    },
                ),
            )
        else:
            additional_fields = (
                self.person_fields
                if obj.type == Contact.TypeChoices.PERSON
                else self.company_fields
            ) + self.common_fields

            return (
                (
                    "General",
                    {"fields": self.generic_fields + additional_fields},
                ),
                (
                    "Consent",
                    {"fields": self.consent_fields},
                ),
            )

    def connected_leads(self, obj=None):
        if obj is None:
            return "-"
        else:
            leads = obj.leads.all()
            if leads:
                leads_html_list = []
                for lead in leads:
                    lead_url = f"crm/lead/{lead.id}/"
                    leads_html_list.append(f'<a href="{lead_url}">{lead}</a>')
                leads_html = "<br>".join(leads_html_list)
                return mark_safe(leads_html)
            else:
                return "-"

    def connected_agent(self, obj=None):
        if obj is None:
            return "-"
        else:
            agent = getattr(obj, "agent", None)
            if agent is None:
                return "-"
            else:
                agent_url = reverse(
                    "admin:real_estate_agent_change", kwargs={"object_id": agent.id}
                )
                return mark_safe(f'<a href="{agent_url}">{agent}</a>')

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if obj is None or request.user.is_superuser:
            return (
                "created_at",
                "updated_at",
            )
        if obj.type == Contact.TypeChoices.PERSON:
            return (
                "created_at",
                "updated_at",
                "type",
                "name",
            )
        else:
            return (
                "created_at",
                "updated_at",
                "type",
                "first_name",
                "last_name",
                "id_card_number",
                "birth_date",
                "gender",
                "job_title",
            )

    def has_history_permission(self, request, obj=None):
        return False


# ------------ LogEntry ------------


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
    fields = (
        "action_time",
        "user",
        "content_type",
        "change_message",
        "action_flag",
        "object_id",
        "object_repr",
    )


admin.site.register(Project, ProjectAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Agreement, AgreementAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Email, EmailAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
