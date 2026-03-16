import datetime
import factory
import random

from random import randint
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from backend.tests import utils
from backend.organization.models import Organization
from backend.real_estate.models import (
    Project,
    RelatedProject,
    ProjectContact,
    PropertyType,
    Property,
    PropertyAssociatedContact,
    PropertyOwner,
    Agreement,
    AgreementRelatedContact,
    AgreementParty,
)
from factory.django import DjangoModelFactory
from factory import fuzzy
from .abstract import AlterCreatedAtFactory


# --------- Project ---------


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.sequence(
        lambda n: f"Project {(n+1)*random.randint(1,100000000000000)}"
    )
    type = fuzzy.FuzzyChoice(choices=[c[0] for c in Project.TypeChoices.choices])
    construction_stage = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Project.ConstructionStageChoices.choices]
    )
    energy_efficiency_grade = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Project.EnergyEfficiencyGradeChoices.choices]
    )
    website_url = factory.Faker("url")
    number_of_units = fuzzy.FuzzyInteger(low=1, high=100)
    location_description = fuzzy.FuzzyText()
    amentities_description = fuzzy.FuzzyText()

    start_date = fuzzy.FuzzyDate(
        start_date=timezone.now().date() + relativedelta(months=-random.randint(4, 8)),
        end_date=timezone.now().date() + relativedelta(months=-random.randint(1, 4)),
    )
    completion_date = fuzzy.FuzzyDate(
        start_date=timezone.now().date() + relativedelta(months=random.randint(1, 8)),
        end_date=timezone.now().date() + relativedelta(months=random.randint(9, 18)),
    )

    starting_price_from = fuzzy.FuzzyDecimal(1000.00, 1000000.00, 2)

    developer = factory.SubFactory("backend.tests.factories.OrganizationFactory")
    address = factory.SubFactory("backend.tests.factories.AddressFactory")

    @factory.post_generation
    def extra_addresses(self, create, extracted, **kwargs):
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return
        self.extra_addresses.add(*extracted)

    @factory.post_generation
    def related_contacts(self, create, extracted, **kwargs):
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return
        for contact in extracted:
            ProjectContact.objects.create(project=self, contact=contact)

    @factory.post_generation
    def related_projects(self, create, extracted, **kwargs):
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return
        for proj in extracted:
            RelatedProject.objects.create(
                project=self,
                related_project=proj,
                relation_type=kwargs.get(
                    "relation", RelatedProject.RelationTypeChoices.CHILD.value
                ),
            )


# --------- Property ---------


class PropertyFactory(DjangoModelFactory):
    class Meta:
        model = Property

    # ForeignKey fields
    type = factory.Iterator(PropertyType.objects.all())
    project = None
    address = factory.SubFactory("backend.tests.factories.AddressFactory")

    # Choices fields
    status = fuzzy.FuzzyChoice(choices=[c[0] for c in Property.StatusChoices.choices])
    utilization = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Property.UtilizationChoices.choices]
    )
    construction_type = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Property.ConstructionTypeChoices.choices]
    )
    construction_stage = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Property.ConstructionStageChoices.choices]
    )
    energy_efficiency_grade = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Property.EnergyEfficiencyGradeChoices.choices]
    )
    electricity_type = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Property.ElectricityTypeChoices.choices]
    )
    heating_type = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Property.EnergyCentralizationChoices.choices]
    )
    heating_medium = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Property.HeatingMediumChoices.choices]
    )
    cooling_type = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Property.EnergyCentralizationChoices.choices]
    )

    # CharFields
    name = factory.LazyAttribute(lambda o: f"Property {random.randint(1,10000000000)}")
    short_description = fuzzy.FuzzyText(length=200)
    description = fuzzy.FuzzyText(length=1000)

    # Boolean and Integer fields
    inherit_project_media = False
    unit_number = fuzzy.FuzzyInteger(1, 100)
    floor = factory.LazyAttribute(lambda o: random.randint(1, o.building_floors))
    building_floors = fuzzy.FuzzyInteger(2, 20)

    parking_spots = factory.LazyAttribute(
        lambda o: o.covered_parking_spots + o.uncovered_parking_spots
    )
    covered_parking_spots = factory.Sequence(lambda n: n)
    uncovered_parking_spots = factory.Sequence(lambda n: n)

    office_spaces = fuzzy.FuzzyInteger(0, 10)

    # DecimalFields
    list_selling_price = fuzzy.FuzzyDecimal(1000.00, 1000000.00, 2)
    list_rental_price = fuzzy.FuzzyDecimal(500.00, 50000.00, 2)

    # IntegerFields
    construction_year = fuzzy.FuzzyInteger(1900, 2015)
    renovation_year = factory.LazyAttribute(
        lambda o: o.construction_year + random.randint(1, 10)
    )

    # FloatFields
    distance_from_school = fuzzy.FuzzyDecimal(0.0, 100.0)
    distance_from_airport = fuzzy.FuzzyDecimal(0.0, 100.0)
    distance_from_university = fuzzy.FuzzyDecimal(0.0, 100.0)
    distance_from_beach = fuzzy.FuzzyDecimal(0.0, 100.0)
    distance_from_hospital = fuzzy.FuzzyDecimal(0.0, 100.0)
    distance_from_shops = fuzzy.FuzzyDecimal(0.0, 100.0)
    distance_from_tube_station = fuzzy.FuzzyDecimal(0.0, 100.0)
    distance_from_rail_station = fuzzy.FuzzyDecimal(0.0, 100.0)
    distance_from_center = fuzzy.FuzzyDecimal(0.0, 100.0)

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            extra_data = kwargs.get("extra_data", [])
            for i, contact in enumerate(extracted):
                PropertyOwner.objects.create(
                    property=self,
                    owner=contact,
                    percentage=extra_data[i].get("percentage"),
                )

    @factory.post_generation
    def associated_contacts(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for contact in extracted:
                PropertyAssociatedContact.objects.create(property=self, contact=contact)


# --------- Agreement ---------


class AgreementFactory(AlterCreatedAtFactory, DjangoModelFactory):
    class Meta:
        model = Agreement

    # Choices fields
    type = fuzzy.FuzzyChoice(choices=[c[0] for c in Agreement.TypeChoices.choices])

    status = Agreement.StatusChoices.OPEN

    # CharFields
    description = factory.Sequence(lambda n: f"description {n}")

    # ForeignKey fields
    assigned_to = factory.SubFactory("backend.tests.factories.UserFactory")
    project = None
    property = factory.SubFactory("backend.tests.factories.PropertyFactory")

    agreement_signing_date = None

    # DecimalFields
    price = fuzzy.FuzzyDecimal(1000.00, 100000.00, 2)

    # DateFields
    valid_from = fuzzy.FuzzyDate(
        utils.NOW.date(), utils.NOW.date() + relativedelta(days=randint(1, 30))
    )
    valid_until = factory.LazyAttribute(
        lambda o: (o.valid_from + relativedelta(months=randint(1, 12)))
        if o.valid_from and o.type != Agreement.TypeChoices.CONTRACT_OF_SALE
        else None
    )

    reservation_date = None

    # m2m
    @factory.post_generation
    def parties(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            extra_data = kwargs.get("extra_data", [{}] * len(extracted))

            for i, contact in enumerate(extracted):
                AgreementParty.objects.create(
                    agreement=self,
                    party=contact,
                    party_type=extra_data[i].get(
                        "party_type", AgreementParty.PartyTypeChoices.BUYER
                    ),
                    percentage_ownership=extra_data[i].get("percentage_ownership", 1),
                    signature_requirement=extra_data[i].get(
                        "signature_requirement", True
                    ),
                    accepted=extra_data[i].get("accepted", True),
                )

    @factory.post_generation
    def related_contacts(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            extra_data = kwargs.get("extra_data", [{}] * len(extracted))
            for i, contact in enumerate(extracted):
                AgreementRelatedContact.objects.create(
                    agreement=self,
                    contact=contact,
                    relation_type=extra_data[i].get(
                        "relation_type",
                        AgreementRelatedContact.RelationTypeChoices.LAWYER,
                    ),
                )

    class Params:
        sale = factory.Trait(type=Agreement.TypeChoices.CONTRACT_OF_SALE.value)
        tenancy = factory.Trait(type=Agreement.TypeChoices.TENANCY_AGREEMENT.value)
        management = factory.Trait(type=Agreement.TypeChoices.PROPERTY_MANAGEMENT.value)
