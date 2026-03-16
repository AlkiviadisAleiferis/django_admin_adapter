import datetime
import factory
from decimal import Decimal
import random
import uuid

from backend.organization.models import User
from backend.common.models import (
    Contact,
    ContactAddress,
    Address,
    Country,
    City,
    Phone,
    Email,
)
from backend.tests import utils
from factory.django import DjangoModelFactory
from factory import fuzzy


class ContactFactory(DjangoModelFactory):
    class Meta:
        model = Contact

    type = Contact.TypeChoices.PERSON.value
    tax_identification_number = factory.LazyAttribute(
        lambda o: f"{112236784+random.random()*10000000000}"
    )
    notes = fuzzy.FuzzyText(length=100)
    name = factory.LazyAttribute(
        lambda o: random.choice(utils.COMPANY_NAME_CHOICES)
        if o.type == Contact.TypeChoices.COMPANY
        else None
    )
    first_name = factory.LazyAttribute(
        lambda o: random.choice(utils.FIRST_NAME_CHOICES)
        if o.type == Contact.TypeChoices.PERSON
        else None
    )
    middle_name = factory.LazyAttribute(
        lambda o: random.choice(utils.FIRST_NAME_CHOICES)
        if o.type == Contact.TypeChoices.PERSON
        else None
    )
    last_name = factory.LazyAttribute(
        lambda o: random.choice(utils.LAST_NAME_CHOICES)
        if o.type == Contact.TypeChoices.PERSON
        else None
    )
    job_title = "job-title"
    gender = factory.LazyAttribute(
        lambda o: Contact.GenderChoices.MALE.value
        if o.type == Contact.TypeChoices.PERSON
        else None
    )
    id_card_number = factory.LazyAttribute(
        lambda o: f"AA{1122334+random.random()*1000000000}"
        if o.type == Contact.TypeChoices.PERSON
        else None
    )
    passport_number = factory.LazyAttribute(
        lambda o: f"{112236784+random.random()*100000000}"
        if o.type == Contact.TypeChoices.PERSON
        else None
    )
    birth_date = None
    preferred_communication_language = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Contact.LanguageChoices.choices]
    )
    preferred_contact_method = fuzzy.FuzzyChoice(
        choices=[c[0] for c in Contact.PreferredContactMethodChoices.choices]
    )

    email_consent = factory.Faker("boolean")
    phone_consent = factory.Faker("boolean")
    sms_consent = factory.Faker("boolean")
    marketing_consent = factory.Faker("boolean")

    country_of_residence = factory.LazyAttribute(
        lambda o: Country.objects.get(slug="greece")
    )
    nationality = factory.LazyAttribute(lambda o: Country.objects.get(slug="greece"))
    email = factory.SubFactory("backend.tests.factories.EmailFactory")
    phone = factory.SubFactory("backend.tests.factories.PhoneFactory")

    class Params:
        person = factory.Trait(
            type=Contact.TypeChoices.PERSON.value,
            first_name=fuzzy.FuzzyChoice(utils.FIRST_NAME_CHOICES),
            middle_name="",
            last_name=fuzzy.FuzzyChoice(utils.LAST_NAME_CHOICES),
            name=None,
        )
        company = factory.Trait(
            type=Contact.TypeChoices.COMPANY.value,
            name=fuzzy.FuzzyChoice(utils.COMPANY_NAME_CHOICES),
            first_name=None,
            middle_name=None,
            last_name=None,
            job_title=None,
            gender=None,
            id_card_number=None,
            passport_number=None,
            birth_date=None,
        )


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    country = "Greece"
    region = "Attiki"
    county = "Attiki"
    postal_code = factory.Sequence(lambda n: f"{12345+n:04d}")
    place = "Athens"
    street = fuzzy.FuzzyText(length=10)
    street_number = factory.Sequence(lambda n: f"{10+n}")

    latitude = fuzzy.FuzzyFloat(37.0, 38.0)
    longitude = fuzzy.FuzzyFloat(23.0, 24.0)


class PhoneFactory(DjangoModelFactory):
    class Meta:
        model = Phone

    number = factory.Sequence(
        lambda n: f"30{6940000000+(n+1)*random.randint(1,100000000000)}"
    )
    country = factory.LazyAttribute(lambda o: Country.objects.get(slug="greece"))
    type = Phone.TypeChoices.MOBILE.value

    class Params:
        mobile = factory.Trait(
            number=factory.Sequence(
                lambda n: f"{306940000000+(n+1)*random.randint(1,10000000000)}"
            ),
            type=Phone.TypeChoices.MOBILE.value,
        )
        landline = factory.Trait(
            number=factory.Sequence(
                lambda n: f"{302100000000+(n+1)*random.randint(1,100000000000)}"
            ),
            type=Phone.TypeChoices.LANDLINE.value,
        )


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Email

    address = factory.Sequence(
        lambda n: f"email{ (n + 1) * int(random.randint(1,1000000000000))}@pytest.com"
    )


class ContactAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactAddress

    contact = factory.SubFactory(ContactFactory)
    country = factory.LazyAttribute(lambda o: Country.objects.get(slug="greece"))
    city = "Athens"
    postal_code = "12345"
    street = factory.Sequence(
        lambda n: f"street { (n + 1) * int(random.randint(1,10000))}"
    )
    street_number = factory.Sequence(
        lambda n: f"{ (n + 1) * int(random.randint(1,10000))}"
    )
    notes = "aaa"
