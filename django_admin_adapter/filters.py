from datetime import datetime, date
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import (
    BigAutoField,
    CharField,
    UUIDField,
    IntegerField,
    PositiveBigIntegerField,
    PositiveSmallIntegerField,
)


def get_modelfield_python_type(model_field_class):
    if isinstance(
        model_field_class,
        (
            BigAutoField,
            IntegerField,
            PositiveBigIntegerField,
            PositiveSmallIntegerField,
        ),
    ):
        return int
    elif isinstance(model_field_class, (CharField, UUIDField)):
        return str
    else:
        raise ImproperlyConfigured(
            f"{model_field_class} field doesn't have a corresponding python type"
        )


class InputFilter(admin.SimpleListFilter):
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

    field_input_type = ""
    input_min = ""
    input_max = ""
    step = ""
    placeholder = ""

    HTML_INPUT_TYPE_MAP = {
        str: "text",
        int: "number",
        float: "number",
        date: "date",
        datetime: "datetime-local",
    }
    FIELD_TYPE_STR = {
        str: "str",
        int: "int",
        float: "float",
        date: "date",
        datetime: "datetime",
    }

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((None, None),)

    def convert_to_internal_value(self, value):
        if self.field_type in {str, int, float}:
            return self.field_type(value)
        elif self.field_type is datetime:
            try:
                return datetime.strptime(value, self.DATETIME_FORMAT)
            except ValueError:
                return datetime.now()
        elif self.field_type is date:
            try:
                return datetime.strptime(value, self.DATE_FORMAT)
            except ValueError:
                return datetime.now()

    def choices(self, changelist):
        query_params = changelist.get_filters_params()
        query_params.pop(self.parameter_name, None)
        all_choice = next(super().choices(changelist))
        all_choice["query_params"] = query_params
        yield all_choice


class AutocompleteFilter(admin.SimpleListFilter):
    """
    An AutocompleteFilter that utilizes an existing
    custom implemented api endpoint for results
    at the `autocomplete_url` endpoint.

    `related_model`: is the related model whose pk \
        is used when searching using the `relation_query_lookup`

    `relation_query_lookup`: the lookup query used for searching. \
        connects the related model to the current one.
    """

    title = None
    parameter_name = None
    disabled_by_default = False

    autocomplete_url = None
    filter_placeholder = ""

    related_model = None
    # is the related model
    # whose pk we need to search with

    relation_query_lookup = None

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)

        if self.related_model is None:
            raise ImproperlyConfigured("'related_model' attribute not set.")

        elif self.related_model not in model_admin.admin_site._registry:
            raise ImproperlyConfigured(
                f"'related_model' provided ({self.related_model}) not registered in admin."
            )

        if self.parameter_name is None:
            raise ImproperlyConfigured(
                "The list filter '%s' does not specify a 'parameter_name'."
                % self.__class__.__name__
            )

        rel_model_name = self.related_model._meta.model_name

        if not model_admin.admin_site._registry[self.related_model].search_fields:
            raise ImproperlyConfigured(
                f"Related model ModelAdmin ({self.related_model}) has no search_fields defined."
            )

        self.autocomplete_url = f"/api/autocomplete/{rel_model_name}/"
        self.set_pk_type()

        if self.relation_query_lookup is None:
            raise ImproperlyConfigured("No lookup query provided")

        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = value

        lookup_choices = self.lookups(request, model_admin)
        if lookup_choices is None:
            lookup_choices = ()
        self.lookup_choices = list(lookup_choices)

    def set_pk_type(self):
        self.pk_type = get_modelfield_python_type(self.related_model._meta.pk)

    def lookups(self, request, model_admin):
        pk = request.GET.get(self.parameter_name)
        self.set_pk_type()

        if not pk:
            return ((None, None),)
        else:
            obj = self.related_model.objects.filter(pk=self.pk_type(pk)).first()
            if obj:
                return (
                    (
                        obj.pk,
                        str(obj),
                    ),
                )
            else:
                return ((None, None),)

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": "All",
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string({self.parameter_name: lookup}),
                "display": title,
            }

    def queryset(self, request, queryset):
        pk = self.value()
        if not pk:
            return
        return queryset.filter(**{self.relation_query_lookup: pk})


# WARNING: when using DateInputFilter with date object
# on datetime field, the date object is converted to datetime
# same date, 00:00:00 HH:MM:ss
# can affect the results!


def build_input_filter(
    field_name: str,
    title: str,
    field_type: str | int | float | date | datetime,
    min_value = None,
    max_value = None,
    lookup_operator: str = "__icontains",
    parameter_name: str | None = None,
    disabled_by_default: bool = False,
    placeholder: str = "",
):
    """
    Returns the proper input filter class according to parameters provided
    params:
        ``field_name``: the name of the field we are filtering for. \
            Will be used inside the query
        ``title``: the filter's title.
        ``field_type``: the python type of field.
        ``min_value``: minimum number or length of text.
        ``max_value``: maximum number or length of text.
        ``lookup_operator``: the lookup operator used on the field.
        ``parameter_name``: custom GET parameter name.
    """
    if parameter_name is None:
        parameter_name = field_name

    if field_type not in InputFilter.FIELD_TYPE_STR:
        raise ImproperlyConfigured(
            f"field type provided '{field_type}' for "
            "input filter is not available"
        )


    filter_title = title
    filter_field_name = field_name
    filter_field_type = field_type
    try:
        filter_field_type_str = InputFilter.FIELD_TYPE_STR[field_type]
    except KeyError:
        raise ImproperlyConfigured(
            "field type provided for input filter is not available"
        )
    filter_parameter_name = parameter_name
    filter_disabled_by_default = disabled_by_default

    html_input_type = InputFilter.HTML_INPUT_TYPE_MAP[field_type]
    html_input_min = min_value
    html_input_max = max_value
    html_step = 1 if field_type is int else None
    html_placeholder = placeholder


    class TypedInputFilter(InputFilter):
        title = f"{filter_title}"
        field_name = f"{filter_field_name}"
        field_type = filter_field_type
        field_type_str = filter_field_type_str
        parameter_name = f"{filter_parameter_name}"
        disabled_by_default = filter_disabled_by_default

        input_type = html_input_type
        input_min = html_input_min
        input_max = html_input_max
        step = html_step
        placeholder = html_placeholder

        def queryset(self, request, queryset):
            value = self.value()  # value provided in GET params
            if not value:
                return
            internal_value = self.convert_to_internal_value(value)
            return queryset.filter(**{filter_field_name + lookup_operator: internal_value})

    return TypedInputFilter


def get_range_filters(
    field_name: str,
    title: str,
    field_type: int|float|date|datetime,
    min_value = None,
    max_value = None,
    parameter_name: str | None = None,
    disabled_by_default: bool = False,
    placeholder: str = "",
) -> tuple[InputFilter, InputFilter]:
    """
    Returns a tuple of two input filters,
    one for the minimum value and one for the maximum value,
    for the provided type (int, float, date, datetime).

    Provide the field_name, title and parameneter_name
    without min/max suffixes.
    These will be appended automatically.
    """

    if parameter_name is None:
        parameter_name = field_name

    if field_type not in (int, float, date, datetime):
        raise ImproperlyConfigured(
            "field type provided for range filter is not available"
        )

    return (
        build_input_filter(
            field_name,
            title + " Minimum",
            field_type,
            min_value=min_value,
            max_value=max_value,
            lookup_operator="__gte",
            parameter_name=parameter_name + "__min",
            disabled_by_default=disabled_by_default,
            placeholder=placeholder,
        ),
        build_input_filter(
            field_name,
            title + " Maximum",
            field_type,
            min_value=min_value,
            max_value=max_value,
            lookup_operator="__lte",
            parameter_name=parameter_name + "__max",
            disabled_by_default=disabled_by_default,
            placeholder=placeholder,
        ),
    )
