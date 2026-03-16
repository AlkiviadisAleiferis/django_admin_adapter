from admin_auto_filters.filters import AutocompleteFilter


class CountryFilter(AutocompleteFilter):
    title = "Country"
    field_name = "country"
    disabled_by_default = False


class NationalityFilter(AutocompleteFilter):
    title = "Nationality"
    field_name = "nationality"
    disabled_by_default = False


class CountryOfResidenceFilter(AutocompleteFilter):
    title = "Country of residence"
    field_name = "country_of_residence"
    disabled_by_default = False


contact_filters = (
    NationalityFilter,
    CountryOfResidenceFilter,
    "type",
    "gender",
    "preferred_communication_language",
    "preferred_contact_method",
    "email_consent",
    "phone_consent",
    "sms_consent",
    "marketing_consent",
)


phone_filters = (CountryFilter,)
