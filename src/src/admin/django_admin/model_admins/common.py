from django.http import HttpRequest
from django.utils.html import format_html
from django.contrib import admin
from backend.common.models import (
    Contact,
    ContactEmployee,
    Phone,
    Email,
    Country,
    Address,
    ContactEmail,
    ContactAddress,
    ContactPhone,
    ContactDocument,
    ContactFile,
    ContactImage,
)

from admin.django_admin.filters.common import contact_filters, phone_filters


# % --------------  Phone  -----------------


class PhoneAdmin(admin.ModelAdmin):
    list_display = ("number", "country", "type")
    fields = ("number", "country", "type")
    search_fields = ("number",)
    list_filter = phone_filters
    verbose_name = "Phone"

    def get_changeform_initial_data(self, request: HttpRequest):
        return {"country": 87}


# % --------------  Email  -----------------


class EmailAdmin(admin.ModelAdmin):
    list_display = ("address",)
    fields = ("address",)
    search_fields = ("address",)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )


# % --------------  Country  -----------------


class CountryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "phone_prefix",
        "alpha_2",
        "alpha_3",
        "numeric",
    )
    fields = ("name", "slug", "phone_prefix", "alpha_2", "alpha_3", "numeric")
    search_fields = ("name", "phone_prefix", "alpha_2", "alpha_3")


# % --------------  Address  -----------------


class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "country",
        "region",
        "county",
        "place",
        "postal_code",
        "street",
        "street_number",
    )
    fields = (
        "country",
        "region",
        "county",
        "place",
        "postal_code",
        "street",
        "street_number",
        "latitude",
        "longitude",
    )
    search_fields = (
        "country",
        "region",
        "county",
        "place",
        "postal_code",
        "street",
        "street_number",
    )


# % --------------  Contact  -----------------


class ContactEmailInline(admin.TabularInline):
    model = ContactEmail
    verbose_name = "Email"
    autocomplete_fields = ("email",)


class ContactPhoneInline(admin.TabularInline):
    model = ContactPhone
    verbose_name = "Phone"
    autocomplete_fields = ("phone",)


class ContactAddressInline(admin.TabularInline):
    model = ContactAddress
    verbose_name = "Address"
    verbose_name_plural = "Addresses"
    autocomplete_fields = ("country",)


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
    )
    list_select_related = (
        "email",
        "phone",
        "nationality",
    )
    list_filter = contact_filters
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
        "country_of_residence",
        "nationality",
        "email",
        "phone",
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

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if obj is None or request.user.is_superuser:
            return (
                "created_at",
                "updated_at",
                "connected_agent",
                "connected_user",
                "connected_leads",
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


admin.site.register(Phone, PhoneAdmin)
admin.site.register(Email, EmailAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Contact, ContactAdmin)
