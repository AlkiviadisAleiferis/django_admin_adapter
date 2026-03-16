"""
Module for constant relations between
    - property category slug
    - corresponding on model fields

Depending on the property.type.category slug
the property's attributes change as expected.

In case of Rooms, Areas and Features a db backed
solution has been given through PropertyCategoryAttribute.

In order to avoid db interactions for now the codebase
implements a mapping on this module.

In later implementation a db backed mapping must be made
for dependency of outside this project interactions.
"""

# ------------------------ ALL CATEGORIES ------------------------
# category slugs provided here are the total
# available in the db

ALL_PROPERTY_CATEGORY_SLUGS = {
    "apartment",
    "house",
    "office",
    "retail",
    "hotel",
    "building",
    "land",
    "other",
}


# ------------------------ BUILDING ------------------------


DEFAULT_BUILDING_FIELDS = (
    "construction_stage",
    "construction_type",
    "construction_year",
    "renovation_year",
    #
    "parking_spots",
    "covered_parking_spots",
    "uncovered_parking_spots",
    #
    "building_floors",
)
BUILDING_FIELDS = DEFAULT_BUILDING_FIELDS + (
    "floor",
    "office_spaces",
    "customer_parking_spots",
)
PROPERTY_CATEGORY_BUILDING_FIELDS_MAPPING = {
    "land": (),
    "apartment": (*DEFAULT_BUILDING_FIELDS, "floor"),
    "house": (*DEFAULT_BUILDING_FIELDS,),
    "office": (*DEFAULT_BUILDING_FIELDS, "floor", "office_spaces"),
    "retail": (*DEFAULT_BUILDING_FIELDS, "floor", "customer_parking_spots"),
    "hotel": (*DEFAULT_BUILDING_FIELDS, "customer_parking_spots"),
    "building": (*DEFAULT_BUILDING_FIELDS,),
    "other": (
        *DEFAULT_BUILDING_FIELDS,
        "floor",
    ),
}

assert set(PROPERTY_CATEGORY_BUILDING_FIELDS_MAPPING) == ALL_PROPERTY_CATEGORY_SLUGS

building_fields = set()

for category in PROPERTY_CATEGORY_BUILDING_FIELDS_MAPPING:
    for field in PROPERTY_CATEGORY_BUILDING_FIELDS_MAPPING[category]:
        building_fields.add(field)

assert set(BUILDING_FIELDS) == building_fields


# ------------------------ ENERGY ------------------------


ENERGY_FIELDS = (
    "energy_efficiency_grade",
    "electricity_type",
    "heating_type",
    "heating_medium",
    "cooling_type",
)
PROPERTY_CATEGORY_ENERGY_FIELDS_MAPPING = {
    "land": (ENERGY_FIELDS[1],),
    "apartment": (*ENERGY_FIELDS,),
    "house": (*ENERGY_FIELDS,),
    "office": (*ENERGY_FIELDS,),
    "retail": (*ENERGY_FIELDS,),
    "hotel": (*ENERGY_FIELDS,),
    "building": (*ENERGY_FIELDS,),
    "other": (*ENERGY_FIELDS,),
}

assert set(PROPERTY_CATEGORY_ENERGY_FIELDS_MAPPING) == ALL_PROPERTY_CATEGORY_SLUGS

energy_fields = set()

for category in PROPERTY_CATEGORY_ENERGY_FIELDS_MAPPING:
    for field in PROPERTY_CATEGORY_ENERGY_FIELDS_MAPPING[category]:
        energy_fields.add(field)

assert set(ENERGY_FIELDS) == energy_fields


# ------------------------ EXTRAS ------------------------


EXTRAS_FIELDS = {
    "awnings",
    "kitchen_type",
    "floor_type",
    "furnished",
    "office_layout",
    "town_planning_zone",
    "cover_factor",
    "building_density",
    "height",
    "ideal_for",
    "licensed_for",
}
PROPERTY_CATEGORY_EXTRAS_FIELDS_MAPPING = {
    "land": (
        "town_planning_zone",
        "cover_factor",
        "building_density",
        "height",
        "ideal_for",
        "licensed_for",
    ),
    "apartment": (
        "awnings",
        "kitchen_type",
        "floor_type",
        "furnished",
    ),
    "house": (
        "awnings",
        "kitchen_type",
        "floor_type",
        "furnished",
    ),
    "office": (
        "floor_type",
        "furnished",
        "office_layout",
    ),
    "retail": (
        "floor_type",
        "kitchen_type",
        "furnished",
    ),
    "hotel": (
        "floor_type",
        "kitchen_type",
    ),
    "building": (
        "floor_type",
        "office_layout",
    ),
    "other": (),
}


assert set(PROPERTY_CATEGORY_EXTRAS_FIELDS_MAPPING) == ALL_PROPERTY_CATEGORY_SLUGS


# check if all the fields in ALL_PROPERTY_DETAILS_JSON_FIELDS
# have been set in PROPERTY_CATEGORY_DETAILS_JSON_FIELDS_MAPPING
all_extras_fields = set()

for category in ALL_PROPERTY_CATEGORY_SLUGS:
    for field in PROPERTY_CATEGORY_EXTRAS_FIELDS_MAPPING[category]:
        all_extras_fields.add(field)

assert all_extras_fields == EXTRAS_FIELDS
