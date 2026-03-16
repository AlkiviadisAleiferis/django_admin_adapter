from datetime import datetime, date
from django.contrib import admin
from django_admin_adapter.filters import (
    build_input_filter,
    get_range_filters,
)
from backend.real_estate.models import Property, Project
from django_admin_adapter.filters import AutocompleteFilter


class PropertyFilter(AutocompleteFilter):
    title = "Property"
    field_name = "property"
    parameter_name = "property"
    related_model = Property

    relation_query_lookup = "property__pk"
    filter_placeholder = "Connected property"


class ProjectFilter(AutocompleteFilter):
    title = "Project"
    field_name = "project"
    parameter_name = "project"
    related_model = Project

    relation_query_lookup = "project__pk"
    filter_placeholder = "Connected project"


agreement_admin_list_filters = (
    PropertyFilter,
    ProjectFilter,
    build_input_filter(
        "description",
        "Description",
        field_type=str,
        disabled_by_default=False,
        parameter_name="description",
    ),
    # property__construction_year
    *get_range_filters(
        "property__construction_year",
        "Property construction year",
        field_type=int,
        disabled_by_default=False,
        parameter_name="property_construction_year",
    ),
    # simple choices
    "type",
    "status",
    # created_at
    *get_range_filters(
        "created_at",
        "Created at",
        field_type=datetime,
        disabled_by_default=False,
    ),
    # agreement_int
    *get_range_filters(
        "agreement_int",
        "Agreement int",
        field_type=int,
        disabled_by_default=False,
        parameter_name="agreement_int",
    ),
    # reservation_date
    *get_range_filters(
        "reservation_date",
        "Reservation date",
        field_type=date,
        disabled_by_default=False,
    ),
    # agreement_signing_date
    *get_range_filters(
        "agreement_signing_date",
        "Signing date",
        field_type=date,
        disabled_by_default=False,
    ),
    # cancel_date
    *get_range_filters(
        "cancel_date",
        "Cancel date",
        field_type=date,
        disabled_by_default=False,
    ),
    # price
    *get_range_filters(
        "price",
        "Price",
        field_type=float,
        disabled_by_default=False,
    ),
    # valid_from
    *get_range_filters(
        "valid_from",
        "Valid from",
        field_type=date,
        disabled_by_default=False,
    ),
    # valid_until
    *get_range_filters(
        "valid_until",
        "Valid until",
        field_type=date,
        disabled_by_default=False,
    ),
)

porperty_list_filters = (ProjectFilter,)
