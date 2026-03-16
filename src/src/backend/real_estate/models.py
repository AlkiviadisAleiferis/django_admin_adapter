from django.core.exceptions import (
    ValidationError,
)
from django.db import models, transaction
from django.db.models import Q

from backend.common.models import (
    NameSlugModel,
    TimeStampedModel,
    DocumentModel,
    FileModel,
    ImageModel,
    Contact,
)
from backend.managers import RelatedNamesManager
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from backend.utils.validators import (
    positive_number_validator,
    less_than_or_equal_to_x_validator,
    greater_than_or_equal_to_x_validator,
)
from . import constants


# % --------------  Abstract  -----------------


class UrbanDistancesModel(models.Model):
    distance_from_school = models.FloatField(
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    distance_from_airport = models.FloatField(
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    distance_from_university = models.FloatField(
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    distance_from_beach = models.FloatField(
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    distance_from_hospital = models.FloatField(
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    distance_from_shops = models.FloatField(
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    distance_from_tube_station = models.FloatField(
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    distance_from_rail_station = models.FloatField(
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    distance_from_center = models.FloatField(
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    distance_from_school = models.FloatField(
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    distance_from_school = models.FloatField(
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )

    class Meta:
        abstract = True


# % --------------  Project  -----------------


class Project(TimeStampedModel, UrbanDistancesModel):
    class EnergyEfficiencyGradeChoices(models.TextChoices):
        PENDING = "PEN", "Pending certification"
        NOT_REQUIRED = "NRQ", "Not required"
        A = "A", "A"
        A_PLUS = "AA", "A+"
        B = "B", "B"
        B_PLUS = "BB", "B+"
        C = "C", "C"
        D = "D", "D"
        E = "E", "E"
        G = "G", "G"
        H = "H", "H"

    class StageChoices(models.TextChoices):
        OFF_PLAN = "OFF", "Off plan"
        UNDER_CONSTRUCTION = "CON", "Under construction"
        STALLED = "STL", "Stalled"
        COMPLETED = "CMP", "Completed"

    class ConstructionStageChoices(models.TextChoices):
        OFF_PLAN = "OFF", "Off plan"
        UNDER_CONSTRUCTION = "CON", "Under construction"
        STALLED = "STL", "Stalled"
        COMPLETE = "CMP", "Completed"

    class TypeChoices(models.TextChoices):
        CONSTRUCTION = "CON", "Construction"

    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=3, choices=TypeChoices.choices)
    construction_stage = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        choices=ConstructionStageChoices.choices,
    )
    energy_efficiency_grade = models.CharField(
        max_length=3, choices=EnergyEfficiencyGradeChoices.choices
    )
    website_url = models.URLField(null=True, blank=True)
    number_of_units = models.PositiveSmallIntegerField(null=True, blank=True)

    location_description = models.TextField(default="", blank=True)
    amentities_description = models.TextField(default="", blank=True)

    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateTimeField(null=True, blank=True)

    starting_price_from = models.DecimalField(
        null=True,
        blank=True,
        max_digits=12,
        decimal_places=2,
        validators=[positive_number_validator],
    )
    comments = models.JSONField(blank=True, default=list)

    developer = models.ForeignKey("organization.Organization", on_delete=models.PROTECT)

    comments = models.JSONField(blank=True, default=list)

    address = models.ForeignKey(
        "common.Address",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="projects",
    )
    extra_addresses = models.ManyToManyField(
        "common.Address",
        through="ProjectAddress",
        related_name="related_projects",
    )

    # m2m
    related_projects = models.ManyToManyField("self", through="RelatedProject")
    related_contacts = models.ManyToManyField(
        "common.Contact", through="ProjectContact", related_name="projects"
    )

    class Meta:
        db_table = "real_estate_project"

    def __str__(self):
        return self.name


class RelatedProject(models.Model):
    class RelationTypeChoices(models.TextChoices):
        BLOCKED_BY = "BLC", "Blocked by"
        EXTENDED_BY = "EXT", "Extends"
        CHILD = "CHL", "Child"

    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    related_project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="related_project"
    )
    relation_type = models.CharField(max_length=3, choices=RelationTypeChoices.choices)
    notes = models.TextField(default="", blank=True)

    class Meta:
        db_table = "related_project"
        unique_together = ["project", "related_project"]

    def __str__(self):
        return f"Project relation: {self.id}"

    def clean(self):
        if (
            self.project is not None
            and self.related_project is not None
            and self.project == self.related_project
        ):
            raise ValidationError("A project cannot relate to itself")


class ProjectAddress(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    address = models.ForeignKey("common.Address", on_delete=models.PROTECT)
    notes = models.TextField(default="", blank=True)

    class Meta:
        db_table = "project_address"
        verbose_name_plural = "Project Addresses"
        unique_together = ["project", "address"]


class ProjectDocument(DocumentModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        db_table = "project_document"

    def infosystem_upload_to(self, filename):
        return f"project/{self.project.pk}/{filename}"


class ProjectFile(FileModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    notes = models.TextField(default="", blank=True)

    class Meta:
        db_table = "project_file"

    def infosystem_upload_to(self, filename):
        return f"project/{self.project.pk}/{filename}"


class ProjectImage(ImageModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    notes = models.TextField(default="", blank=True)

    class Meta:
        db_table = "project_image"

    def infosystem_upload_to(self, filename):
        return f"project/{self.project.pk}/{filename}"


class ProjectContact(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    contact = models.ForeignKey("common.Contact", on_delete=models.CASCADE)
    notes = models.TextField(default="", blank=True)

    class Meta:
        db_table = "project_contact"
        unique_together = ["project", "contact"]


# % --------------  Property Category/Types  -----------------


class PropertyCategory(NameSlugModel):
    class Meta:
        db_table = "property_category"
        verbose_name = "Property category"
        verbose_name_plural = "Property categories"


class PropertyType(NameSlugModel):
    category = models.ForeignKey(PropertyCategory, on_delete=models.PROTECT)

    objects = RelatedNamesManager(select_related_names=("category",))
    objects_ = models.Manager()

    class Meta:
        db_table = "property_type"

    def __str__(self):
        return f"{self.category} - {self.name}"


# % --------------  Property  -----------------


class Property(
    TimeStampedModel,
    UrbanDistancesModel,
    ImageModel,
):
    class StatusChoices(models.TextChoices):
        PENDING = "PND", "Pending"
        AVAILABLE = "AVL", "Available"
        RESERVED = "RSV", "Reserved"
        SOLD = "SLD", "Sold"
        RENTED = "RNT", "Rented"
        WITHDRAWN = "WTH", "Withdrawn"
        UNDER_OFFER = "OFF", "Under offer"

    class UtilizationChoices(models.TextChoices):
        SALE = "SL", "Sale"
        RENT = "RNT", "Rent"
        SALE_AND_RENT = "SNR", "Sale and Rent"
        MANAGE = "MNG", "Manage"
        AUCTION = "AUC", "Auction"

    class ConstructionTypeChoices(models.TextChoices):
        CONCRETE = "CNR", "Concrete"
        PREFABRICATED = "PFB", "Prefabricated"
        METAL = "MTL", "Metal"

    class ConstructionStageChoices(models.TextChoices):
        OFF_PLAN = "OFF", "Off plan"
        UNDER_CONSTRUCTION = "CON", "Under construction"
        UNFINISHED = "UNF", "Unfinished"
        COMPLETE = "CMP", "Complete"
        RESALE = "RSL", "Resale"

    class ElectricityTypeChoices(models.TextChoices):
        SINGLE_PHASE = "SP", "Single phase"
        THREE_PHASE = "TP", "Three phase"
        INDUSTRIAL = "IN", "Industrial"
        UNAVAILABLE = "NA", "Unavailable"

    class EnergyCentralizationChoices(models.TextChoices):
        AUTONOMOUS = "AUT", "Autonomous"
        CENTRAL = "CNT", "Central"

    class HeatingMediumChoices(models.TextChoices):
        PETROL = "PTR", "Petrol"
        GAS = "GS", "Gas"
        BOTTLE_GAS_LPG = "BGS", "Bottle Gas-LPG"
        ELECTRIC = "EL", "Electric"
        UNDERFLOOR = "UFL", "Underfloor"
        STORAGE = "STR", "Storage"
        HEAT_PUMP = "HPM", "Heat pump"
        GEOTHERMAL = "GTH", "Geothermal"
        FAN_COIL = "FCL", "Fan coil"
        SOLAR = "SLR", "Solar"
        OIL = "OIL", "Oil"

    class EnergyEfficiencyGradeChoices(models.TextChoices):
        PENDING = "PEN", "Pending certification"
        NOT_REQUIRED = "NRQ", "Not required"
        A = "A", "A"
        A_PLUS = "AA", "A+"
        B = "B", "B"
        B_PLUS = "BB", "B+"
        C = "C", "C"
        D = "D", "D"
        E = "E", "E"
        G = "G", "G"
        H = "H", "H"

    class AwningsChoices(models.TextChoices):
        MANUAL = "MAN", "Manual"
        ELECTRIC = "EL", "Electric"
        NA = "NA", "Non available"

    class FloorTypeChoices(models.TextChoices):
        MARBLE = "MAR", "Marble"
        TILES = "TIL", "Tiles"
        WOODEN = "WDN", "Wooden floor"
        GRANITE = "GRN", "Granite"
        INDUSTRIAL = "IND", "Industrial"
        MOSAIC = "MOS", "Mosaic"
        LAMINATE = "LAM", "Laminate"
        PARQUET = "PAR", "Parquet"

    class FurnishedChoices(models.TextChoices):
        FULLY = "FUL", "Fully"
        PARTIALLY = (
            "PAR",
            "Partially",
        )
        OPTIONALLY = "OPT", "Optionally"
        UNFURNISHED = "NO", "Unfurnished"

    class KitchenTypeChoices(models.TextChoices):
        OPEN_PLAN = "OPP", "Open plan"
        SEPERATED = "SEP", "Seperated"

    class OfficeLayoutChoices(models.TextChoices):
        OPEN_PLAN = "OP", "Open plan"
        PARTITIONED = "PRT", "Partitioned"
        SHELL_AND_CORE = "SHC", "Shell and core"

    class TownPlanningZoneChoices(models.TextChoices):
        RESIDENTIAL = (
            "RES",
            "Residential",
        )
        COMMERCIAL = "COM", "Commercial"
        INDUSTRIAL = "IND", "Industrial"
        AGRICULTURAL = "AGR", "Agricultural"
        TOURIST = "TRS", "Tourist"
        OTHER = "OTH", "Other"

    objects = RelatedNamesManager(select_related_names=("type__category",))
    objects_ = models.Manager()

    # MAIN DATA
    type = models.ForeignKey(PropertyType, on_delete=models.PROTECT)
    status = models.CharField(max_length=3, choices=StatusChoices.choices)
    utilization = models.CharField(max_length=3, choices=UtilizationChoices.choices)

    name = models.CharField(max_length=100, unique=True, help_text="English only")
    short_description = models.CharField(
        max_length=200, default="", blank=True, help_text="English only"
    )
    description = models.TextField(default="", blank=True, help_text="English only")

    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.PROTECT)
    inherit_project_media = models.BooleanField(default=False)
    unit_number = models.PositiveSmallIntegerField(null=True, blank=True)

    list_selling_price = models.DecimalField(
        null=True,
        blank=True,
        max_digits=12,
        decimal_places=2,
        validators=[positive_number_validator],
    )
    list_rental_price = models.DecimalField(
        null=True,
        blank=True,
        max_digits=12,
        decimal_places=2,
        validators=[positive_number_validator],
    )

    assigned_to = models.ForeignKey(
        "organization.User", null=True, blank=True, on_delete=models.SET_NULL
    )
    address = models.ForeignKey(
        "common.Address", null=True, blank=True, on_delete=models.PROTECT
    )

    # ATTRIBUTES FIELDS
    # building details
    construction_year = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            greater_than_or_equal_to_x_validator(1900),
            less_than_or_equal_to_x_validator(2060),
        ],
        help_text="If not construction complete, this is estimated year",
    )
    construction_type = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        choices=ConstructionTypeChoices.choices,
    )
    construction_stage = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        choices=ConstructionStageChoices.choices,
    )
    renovation_year = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            greater_than_or_equal_to_x_validator(1900),
            less_than_or_equal_to_x_validator(2060),
        ],
        help_text="Greater than construction year.",
    )

    # building/floor
    floor = models.PositiveSmallIntegerField(null=True, blank=True)
    building_floors = models.PositiveSmallIntegerField(null=True, blank=True)

    # building/parking
    parking_spots = models.PositiveSmallIntegerField(null=True, blank=True)
    covered_parking_spots = models.PositiveSmallIntegerField(null=True, blank=True)
    uncovered_parking_spots = models.PositiveSmallIntegerField(null=True, blank=True)
    customer_parking_spots = models.PositiveSmallIntegerField(null=True, blank=True)

    # building/energy
    energy_efficiency_grade = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        choices=EnergyEfficiencyGradeChoices.choices,
    )
    electricity_type = models.CharField(
        max_length=3,
        default=ElectricityTypeChoices.UNAVAILABLE,
        blank=True,
        choices=ElectricityTypeChoices.choices,
    )
    heating_type = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        choices=EnergyCentralizationChoices.choices,
    )
    heating_medium = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        choices=HeatingMediumChoices.choices,
    )
    cooling_type = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        choices=EnergyCentralizationChoices.choices,
    )

    # building/extra
    office_spaces = models.PositiveSmallIntegerField(null=True, blank=True)

    # extra fields
    awnings = models.CharField(
        max_length=3, choices=AwningsChoices.choices, null=True, blank=True
    )
    floor_type = models.CharField(
        max_length=3, choices=FloorTypeChoices.choices, null=True, blank=True
    )
    furnished = models.CharField(
        max_length=3, choices=FurnishedChoices.choices, null=True, blank=True
    )
    kitchen_type = models.CharField(
        max_length=3, choices=KitchenTypeChoices.choices, null=True, blank=True
    )
    office_layout = models.CharField(
        max_length=3, choices=OfficeLayoutChoices.choices, null=True, blank=True
    )
    town_planning_zone = models.CharField(
        max_length=3, choices=TownPlanningZoneChoices.choices, null=True, blank=True
    )
    cover_factor = models.FloatField(
        validators=[positive_number_validator], null=True, blank=True
    )
    building_density = models.FloatField(
        validators=[positive_number_validator], null=True, blank=True
    )
    height = models.FloatField(
        validators=[positive_number_validator], null=True, blank=True
    )
    ideal_for = models.CharField(max_length=300, null=True, blank=True)
    licensed_for = models.CharField(max_length=300, null=True, blank=True)

    comments = models.JSONField(blank=True, default=list)

    # m2m
    owners = models.ManyToManyField(
        "common.Contact",
        through="PropertyOwner",
        related_name="owner_properties",
    )
    associated_contacts = models.ManyToManyField(
        "common.Contact",
        through="PropertyAssociatedContact",
        related_name="associated_properties",
    )

    class Meta:
        db_table = "property"
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.name} [ID:{self.id}]"

    def infosystem_upload_to(self, filename):
        return f"property/{self.pk}/{filename}"

    def clean(self):
        if self.type is None:
            raise ValidationError({"type": "No type provided."})

        category_slug = self.type.category.slug
        # for every attribute that does not belong to this category
        # set it to null
        if category_slug in constants.ALL_PROPERTY_CATEGORY_SLUGS:
            category_building_fields = set(
                constants.PROPERTY_CATEGORY_BUILDING_FIELDS_MAPPING[category_slug]
            )
            category_energy_fields = set(
                constants.PROPERTY_CATEGORY_ENERGY_FIELDS_MAPPING[category_slug]
            )
            non_category_building_fields = set(constants.BUILDING_FIELDS).difference(
                category_building_fields
            )
            non_category_energy_fields = set(constants.ENERGY_FIELDS).difference(
                category_energy_fields
            )
            for field in non_category_building_fields.union(non_category_energy_fields):
                setattr(self, field, None)

        if not (
            (self.parking_spots or 0)
            == sum(
                [
                    self.uncovered_parking_spots or 0,
                    self.covered_parking_spots or 0,
                    self.customer_parking_spots or 0,
                ]
            )
        ):
            raise ValidationError(
                "Parking spots sizes do not  match. Uncovered, covered and customer parking spots must equate to Parking spots."
            )

        if self.building_floors is not None and self.building_floors < 0:
            raise ValidationError(
                {"building_floors": "Building floors cannot be negative."}
            )

        if self.floor is not None and self.building_floors is None:
            raise ValidationError({"floor": "Building floors must be set."})

        if self.floor is not None and self.building_floors is not None:
            if self.floor < 0:
                raise ValidationError({"floor": "Floor cannot be negative."})

            if self.floor > self.building_floors:
                raise ValidationError(
                    {"floor": "Floor cannot be greater than the max building floor."}
                )

        if self.renovation_year is not None and self.construction_year is None:
            raise ValidationError({"renovation_year": "Construction year must be set."})

        if (
            self.renovation_year is not None
            and self.construction_year is not None
            and self.renovation_year <= self.construction_year
        ):
            raise ValidationError(
                {
                    "renovation_year": "Renovation year cannot be earlier than construction year."
                }
            )

    def can_change_owners(self, force_check=False):
        # be aware that this caching mechanism
        # can give wrong results after m2m update
        if not hasattr(self, "_can_change_owners") or force_check:
            self._can_change_owners = not Agreement.objects.filter(
                status__in=(
                    Agreement.StatusChoices.OPEN,
                    Agreement.StatusChoices.AGREED,
                    Agreement.StatusChoices.RESERVED,
                ),
                property=self,
            ).exists()

        return self._can_change_owners


class PropertyAssociatedContact(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    contact = models.ForeignKey("common.Contact", on_delete=models.CASCADE)
    notes = models.TextField(default="", blank=True)

    objects = RelatedNamesManager(select_related_names=("property", "contact"))

    class Meta:
        db_table = "property_associated_contact"
        verbose_name = "Property Contact"
        unique_together = ["property", "contact"]

    def __str__(self):
        return str(self.contact)


class PropertyOwner(TimeStampedModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="property_owners"
    )
    owner = models.ForeignKey(
        "common.Contact", on_delete=models.CASCADE, related_name="properties_ownerships"
    )
    percentage = models.FloatField(
        validators=[
            positive_number_validator,
            less_than_or_equal_to_x_validator(1),
        ]
    )

    class Meta:
        db_table = "property_owner"
        verbose_name = "Property Owner"
        unique_together = ["property", "owner"]

    def __str__(self):
        return f"(Property id:{self.property_id}) (Contact id:{self.owner_id}) {self.percentage*100}%"


class PropertyDocument(DocumentModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

    class Meta:
        db_table = "property_document"

    def infosystem_upload_to(self, filename):
        return f"property/{self.property.pk}/{filename}"


class PropertyFile(FileModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    notes = models.TextField(default="", blank=True)

    class Meta:
        db_table = "property_file"

    def infosystem_upload_to(self, filename):
        return f"property/{self.property.pk}/{filename}"


class PropertyImage(ImageModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    notes = models.TextField(default="", blank=True)

    class Meta:
        db_table = "property_image"

    def infosystem_upload_to(self, filename):
        return f"property/{self.property.pk}/{filename}"


# % --------------  Agreement  -----------------


class Agreement(
    TimeStampedModel,
):
    class TypeChoices(models.TextChoices):
        CONTRACT_OF_SALE = "COS", "Contract of Sale"
        TENANCY_AGREEMENT = "TEN", "Tenancy Agreement"
        PROPERTY_MANAGEMENT = "PMG", "Property management Agreement"

    class StatusChoices(models.TextChoices):
        OPEN = "OPN", "Open"
        RESERVED = "RSV", "Reserved"
        CANCELLED = "CNL", "Cancelled"
        AGREED = "AGR", "Agreed"

    class PaymentPeriodChoices(models.TextChoices):
        DAY = "D", "Day"
        MONTH = "M", "Month"
        YEAR = "Y", "Agreed"

    type = models.CharField(
        max_length=3,
        help_text="type after creation gets locked",
        choices=TypeChoices.choices,
    )
    status = models.CharField(
        max_length=3,
        choices=StatusChoices.choices,
        help_text=(
            "After setting to Agreed or Cancelled, "
            "<br>the Agreement gets locked and cannot be edited"
        ),
    )
    agreement_signing_date = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "If a date is provided, the agreement will be thought as accepted. <br>"
            "This will lock the agreement for edit."
        ),
    )
    signing_time = models.TimeField(null=True, blank=True)

    # valid periods
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    cancel_date = models.DateField(null=True, blank=True)
    description = models.TextField(default="", blank=True)

    # ForeignKey fields
    assigned_to = models.ForeignKey(
        "organization.User",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="agreements",
    )
    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="agreements",
    )
    property = models.ForeignKey(
        Property,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="agreements",
    )

    unique_id = models.UUIDField(null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    closure_percentage = models.FloatField(null=True, blank=True)
    agreement_int = models.IntegerField(
        null=True, blank=True, default=1, help_text="needed an integer field"
    )

    has_private_agreement = models.BooleanField(null=True, blank=True)
    private_agreement_date = models.DateField(null=True, blank=True)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    down_payment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[positive_number_validator],
    )
    reservation_date = models.DateField(null=True, blank=True)

    # m2m
    parties = models.ManyToManyField(
        "common.Contact",
        through="AgreementParty",
        related_name="party_agreements",
    )
    related_contacts = models.ManyToManyField(
        "common.Contact",
        through="AgreementRelatedContact",
        related_name="related_agreements",
    )

    class Meta:
        db_table = "agreement"

    def __str__(self):
        return f"{self.get_type_display()} [ID {self.id}]"

    def clean(self):
        # -------- valid_from/until validation --------
        if self.valid_until is not None and self.valid_from is None:
            raise ValidationError(
                {"valid_until": "Valid until cannot be set if valid form is null."}
            )
        elif (
            self.valid_from is not None
            and self.valid_until is not None
            and self.valid_from >= self.valid_until
        ):
            raise ValidationError("Valid until cannot be before valid from.")

        # ----------- type validation --------------------
        if self.type == self.TypeChoices.CONTRACT_OF_SALE:
            if self.valid_until:
                raise ValidationError(
                    {"valid_until": "A contract of sale does not expire."}
                )

        elif self.type == self.TypeChoices.TENANCY_AGREEMENT:
            if self.valid_from is None:
                raise ValidationError({"valid_from": "A tenancy agreement must start."})
            elif self.valid_until is None:
                raise ValidationError({"valid_until": "A tenancy agreement must end."})

        elif self.type == self.TypeChoices.PROPERTY_MANAGEMENT:
            if self.valid_from is None:
                raise ValidationError(
                    {"valid_from": "A management agreement must start."}
                )
            elif self.valid_until is None:
                raise ValidationError({"valid_until": "A management agreement must end."})


class AgreementCommission(TimeStampedModel):
    agreement = models.ForeignKey(
        Agreement, on_delete=models.CASCADE, related_name="commissions"
    )

    beneficiary = models.ForeignKey(
        "common.Contact",
        on_delete=models.PROTECT,
    )
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[positive_number_validator],
    )

    class Meta:
        db_table = "agreement_commission"

    def clean(self):
        if self.beneficiary_id and self.beneficiary.type != Contact.TypeChoices.COMPANY:
            raise ValidationError("Beneficiary must be a company.")


class AgreementRelatedContact(models.Model):
    class RelationTypeChoices(models.TextChoices):
        LAWYER = "LAW", "Lawyer"
        LAW_FIRM = "LWF", "Lawyer firm"
        OTHER = "OTH", "Other"

    relation_type = models.CharField(max_length=3, choices=RelationTypeChoices.choices)
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE)
    contact = models.ForeignKey("common.Contact", on_delete=models.PROTECT)
    notes = models.TextField(default="", blank=True)

    class Meta:
        db_table = "agreement_related_contact"
        unique_together = ["agreement", "contact"]

    def __str__(self):
        return f"Agreement (id-{self.agreement_id}) related contact id: {self.contact_id}"


class AgreementParty(models.Model):
    class PartyTypeChoices(models.TextChoices):
        BUYER = "BUY", "Buyer"
        SELLER = "SLR", "Seller"
        LANDLORD = "LND", "Landlord"
        TENANT = "TNT", "Tenant"
        MANAGER = "MNG", "Manager"
        REPRESENTATIVE = "RPR", "Representative"
        LAWYER = "LWR", "Lawyer"

    agreement = models.ForeignKey(
        Agreement, on_delete=models.CASCADE, related_name="agreement_parties"
    )
    party = models.ForeignKey(
        "common.Contact", on_delete=models.PROTECT, related_name="involved_agreements"
    )

    party_type = models.CharField(max_length=3, choices=PartyTypeChoices.choices)
    signature_requirement = models.BooleanField(default=False)
    percentage_ownership = models.FloatField(
        null=True,
        blank=True,
        validators=[
            positive_number_validator,
            less_than_or_equal_to_x_validator(1),
        ],
    )
    notes = models.TextField(default="", blank=True)
    accepted = models.BooleanField(default=False)

    # objects = RelatedNamesManager(select_related_names=("agreement", "party"))

    class Meta:
        db_table = "agreement_party"
        verbose_name_plural = "Agreement Parties"
        unique_together = ["agreement", "party"]


class AgreementDocument(DocumentModel):
    class TypeChoices(models.TextChoices):
        PRIVATE = "PRV", "Private agreement document"
        CONTRACT = "CNT", "Contract document"
        BANK = "BNK", "Bank document"
        ADMIN_API = "CLN", "Client portal document"
        OTHER = "OTH", "Other"

    type = models.CharField(
        max_length=3,
        default=TypeChoices.PRIVATE,
        choices=TypeChoices.choices,
    )

    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE)

    class Meta:
        db_table = "agreement_document"

    def infosystem_upload_to(self, filename):
        return f"agreement/{self.agreement.pk}/{filename}"
