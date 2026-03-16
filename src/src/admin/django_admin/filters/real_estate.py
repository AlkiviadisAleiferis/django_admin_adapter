from datetime import date
from django.contrib import admin
from django.db.models import Q
from slugify import slugify
from admin_auto_filters.filters import AutocompleteFilter


# % ------------------ Property / Agreement ------------------


class PropertyFilter(AutocompleteFilter):
    title = "Property"
    field_name = "property"


class ProjectFilter(AutocompleteFilter):
    title = "Project"
    field_name = "project"


class AssignedToFilter(AutocompleteFilter):
    title = "Assignee"
    field_name = "assigned_to"


agreement_admin_list_filters = (
    "type",
    "status",
    AssignedToFilter,
    PropertyFilter,
    ProjectFilter,
)


property_admin_list_filters = (
    "type__category",
    "status",
    "utilization",
    "construction_type",
    "construction_stage",
    "energy_efficiency_grade",
    "electricity_type",
    "heating_type",
    "heating_medium",
    "cooling_type",
    # autocomplete
    AssignedToFilter,
    # details
    "awnings",
    "floor_type",
    "office_layout",
    "kitchen_type",
    "furnished",
    "town_planning_zone",
)
