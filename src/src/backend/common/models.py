from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
import slugify
from backend.utils.validators import (
    clean_file_field,
)
from backend.utils.files import infosys_upload_to


# % --------------  abstract  -----------------


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class NameSlugModelManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class NameSlugModel(models.Model):
    objects = NameSlugModelManager()

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=200)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.create_slug()
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.slug,)

    def create_slug(self):
        self.slug = slugify.slugify(self.name)


class ImageModel(models.Model):
    image = models.ImageField(
        max_length=255, null=True, blank=True, upload_to=infosys_upload_to
    )

    class Meta:
        abstract = True

    def clean(self):
        clean_file_field(self, "image")


class FileModel(models.Model):
    file = models.FileField(max_length=255, upload_to=infosys_upload_to)

    class Meta:
        abstract = True

    def clean(self):
        clean_file_field(self, "file")


class DocumentType(NameSlugModel):
    class Meta:
        db_table = "document_type"


class DocumentModel(FileModel):
    class TypeChoices(models.TextChoices):
        PRIVATE = "PRV", "Private agreement document"
        CONTRACT = "CNT", "Contract document"
        BANK = "BNK", "Bank document"
        ADMIN_API = "CLN", "Client portal document"
        ADVERTISEMENT = "ADV", "Advertisement"
        BILL = "BLL", "Bill"
        OTHER = "OTH", "Other"

    identifier = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=3, choices=TypeChoices.choices)
    issuer = models.CharField(max_length=100)
    issued_at = models.DateField(null=True, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    notes = models.TextField(default="", blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.identifier}"

    def clean(self):
        clean_file_field(self, "file")


# % --------------  Country  -----------------


class Country(NameSlugModel):
    phone_prefix = models.CharField(max_length=15, null=True)
    alpha_2 = models.CharField(max_length=2, unique=True)
    alpha_3 = models.CharField(max_length=3, unique=True)
    numeric = models.CharField(max_length=3, unique=True)
    region = models.CharField(max_length=20)
    sub_region = models.CharField(max_length=50)

    class Meta:
        db_table = "country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return f"{self.name} (+{self.phone_prefix})"


class City(NameSlugModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        db_table = "city"
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name


# % --------------  Address  -----------------


class Address(models.Model):
    country = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    place = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    street_number = models.CharField(max_length=10)

    latitude = models.FloatField(null=True, blank=True, help_text="the North coordinate")
    longitude = models.FloatField(null=True, blank=True, help_text="the East coordinate")

    class Meta:
        db_table = "address"
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.street} {self.street_number}, {self.postal_code} {self.place}, {self.region} {self.country}"


# % --------------  Phone/Email  -----------------


class Phone(models.Model):
    class TypeChoices(models.TextChoices):
        MOBILE = "M", "Mobile"
        LANDLINE = "L", "Landline"

    number = models.CharField(max_length=20, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TypeChoices.choices)

    class Meta:
        db_table = "phone"

    def __str__(self):
        return self.number

    def clean(self):
        if self.number is None:
            raise ValidationError({"number": "number is missing."})
        if getattr(self, "country", None) is None:
            raise ValidationError({"country": "country is missing."})
        if self.type is None:
            raise ValidationError({"type": "type is missing."})

        if not self.number.isdigit():
            raise ValidationError({"number": "Only numbers allowed."})

        phone_prefix = self.country.phone_prefix

        if "," in phone_prefix:
            valid_phone_prefixes = phone_prefix.split(",")
            one_found = False
            for valid_phone_prefix in valid_phone_prefixes:
                if self.number.startswith(valid_phone_prefix):
                    one_found = True
                    break
            if not one_found:
                raise ValidationError(
                    {"number": "number does not start with country prefix."}
                )
        else:
            if not self.number.startswith(phone_prefix):
                raise ValidationError(
                    {"number": "number does not start with country prefix."}
                )


class Email(models.Model):
    address = models.EmailField(max_length=50, unique=True)

    class Meta:
        db_table = "email"

    def __str__(self):
        return self.address


# % --------------  Contact  -----------------


class Contact(TimeStampedModel):
    class TypeChoices(models.TextChoices):
        COMPANY = "C", "Company"
        PERSON = "P", "Person"

    class GenderChoices(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    class LanguageChoices(models.TextChoices):
        GREEK = "GR", "Greek"
        ENGLISH = "EN", "English"

    class PreferredContactMethodChoices(models.TextChoices):
        MOBILE = "MOB", "Mobile"
        HOME_PHONE = "HMP", "Home phone"
        WORK_PHONE = "WKP", "Work phone"
        EMAIL = "EML", "Email"
        SMS = "SMS", "SMS"
        VIBER = "VIB", "Viber"
        WHATSUP = "WHA", "What's up"
        TELEGRAM = "TLG", "Telegram"
        OTHER = "OTH", "Other"

    type = models.CharField(max_length=1, choices=TypeChoices.choices)
    tax_identification_number = models.CharField(
        max_length=20, null=True, blank=True, unique=True
    )
    notes = models.TextField(default="", blank=True)

    # ForeignKey
    country_of_residence = models.ForeignKey(
        "common.Country",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="residents",
    )
    nationality = models.ForeignKey(
        "common.Country",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="nationals",
    )
    email = models.ForeignKey(
        "common.Email", null=True, blank=True, on_delete=models.SET_NULL
    )
    phone = models.ForeignKey(
        "common.Phone", null=True, blank=True, on_delete=models.SET_NULL
    )

    # company attributes
    name = models.CharField(
        max_length=30, null=True, blank=True, help_text="company name"
    )

    # person attributes
    first_name = models.CharField(max_length=30, null=True, blank=True)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    job_title = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(
        max_length=1, null=True, blank=True, choices=GenderChoices.choices
    )
    id_card_number = models.CharField(max_length=30, null=True, blank=True, unique=True)
    passport_number = models.CharField(max_length=30, null=True, blank=True, unique=True)
    birth_date = models.DateField(null=True, blank=True)

    # common company/person attrs
    preferred_communication_language = models.CharField(
        max_length=2, choices=LanguageChoices.choices
    )
    preferred_contact_method = models.CharField(
        max_length=3, choices=PreferredContactMethodChoices.choices
    )

    # consent
    email_consent = models.BooleanField(default=False)
    phone_consent = models.BooleanField(default=False)
    sms_consent = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)

    # m2m
    extra_phones = models.ManyToManyField(
        "common.Phone", through="ContactPhone", related_name="contacts"
    )
    extra_emails = models.ManyToManyField(
        "common.Email", through="ContactEmail", related_name="contacts"
    )
    employees = models.ManyToManyField("self", through="ContactEmployee")

    class Meta:
        db_table = "contact"

    def __str__(self):
        if self.type == self.TypeChoices.COMPANY:
            return f"{self.name} [ID-{self.id}]"
        else:
            if self.middle_name:
                return f"{self.first_name} {self.middle_name} {self.last_name} (id-{self.id})"
            else:
                return f"{self.first_name} {self.last_name} (id-{self.id})"

    def clean(self):
        if self.id is None:
            if self.type == self.TypeChoices.COMPANY:
                self.first_name, self.last_name, self.middle_name = None, None, None
                self.job_title, self.id_card_number, self.passport_number = (
                    None,
                    None,
                    None,
                )
                self.birth_date, self.gender = None, None
            else:
                self.name = None


class ContactEmployee(models.Model):
    class PositionChoices(models.TextChoices):
        CEO = "CEO", "CEO"
        BOARD_MEMBER = "BRD", "Board member"
        DIRECTOR = "DRC", "Director"
        MANAGER = "MNG", "Manager"
        SALES = "SLS", "Sales"
        OTHER = "OTH", "Other"

    employer = models.ForeignKey(
        Contact,
        on_delete=models.PROTECT,
        related_name="contact_employees",
        limit_choices_to={"type": Contact.TypeChoices.COMPANY},
    )
    employee = models.ForeignKey(
        Contact,
        on_delete=models.PROTECT,
        related_name="contact_employers",
        limit_choices_to={"type": Contact.TypeChoices.PERSON},
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    position = models.CharField(null=True, blank=True, choices=PositionChoices.choices)

    class Meta:
        db_table = "contact_employee"
        unique_together = ["employer", "employee"]

    def __str__(self):
        return f"Contact employment (ID:{self.id})"

    def clean(self):
        if self.employer_id is None:
            raise ValidationError("Contact must not be empty.")
        if self.employer.type != Contact.TypeChoices.COMPANY:
            raise ValidationError({"contact": "Only a company can have employees."})

        if self.employee_id is None:
            raise ValidationError("Employee must not be empty.")
        if self.employee.type == Contact.TypeChoices.COMPANY:
            raise ValidationError(
                {"employee": "A company cannot have other companies as employees."}
            )


class ContactPhone(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    phone = models.OneToOneField("common.Phone", on_delete=models.CASCADE)

    class Meta:
        db_table = "contact_phone"
        unique_together = ["contact", "phone"]


class ContactEmail(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    email = models.OneToOneField(
        "common.Email",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "contact_email"
        unique_together = ["contact", "email"]


class ContactAddress(models.Model):
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="addresses"
    )
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    city = models.CharField(max_length=30)
    postal_code = models.CharField(max_length=10)
    street = models.CharField(max_length=50)
    street_number = models.CharField(max_length=10)
    notes = models.TextField(default="", blank=True)

    class Meta:
        db_table = "contact_address"
        verbose_name_plural = "Contact Addresses"

    def __str__(self):
        return f"{self.contact}: {self.street} {self.street_number}, {self.postal_code}, {self.city}"


class ContactDocument(DocumentModel):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)

    class Meta:
        db_table = "contact_document"

    def infosystem_upload_to(self, filename):
        return f"contact/{self.contact.pk}/{filename}"


class ContactFile(FileModel):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    notes = models.TextField(default="", blank=True)

    class Meta:
        db_table = "contact_file"

    def infosystem_upload_to(self, filename):
        return f"contact/{self.contact.pk}/{filename}"


class ContactImage(ImageModel):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    notes = models.TextField(default="", blank=True)

    class Meta:
        db_table = "contact_image"

    def infosystem_upload_to(self, filename):
        return f"contact/{self.contact.pk}/{filename}"
