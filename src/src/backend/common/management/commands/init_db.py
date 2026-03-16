import os
from slugify import slugify

from django.contrib.auth.models import Group
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.db import transaction

from . import permissions_map
from backend.archive.models import DocumentType
from backend.common.models import Contact
from backend.organization.models import User, Organization


DEFAULT_INIT_PASS = "asd!@#123"


class Command(BaseCommand):
    help = "Initialize the db to the required initial state"
    GROUPS = (
        "Admins",
        "Management",
        "Sales",
        "After-sales",
        "Legal",
    )

    def create_document_types(self):
        print("-- installing Document Types:")
        DocumentType.objects.get_or_create(name="Contract", slug="contract")
        DocumentType.objects.get_or_create(name="Agreement", slug="agreement")
        DocumentType.objects.get_or_create(name="Bill", slug="bill")
        DocumentType.objects.get_or_create(
            name="Identification document", slug="identification-document"
        )
        DocumentType.objects.get_or_create(
            name="Company document", slug="company-document"
        )
        print("\tDone!\n")

    def create_users(self):
        print("-- installing basic Users:")
        users_str = os.environ.get("INIT_USERS")
        print(users_str)
        users = eval(users_str)
        for username, first_Name, last_name, group_name in users:
            if not User.objects.filter(username=username).exists():
                self.create_user(
                    username,
                    first_Name,
                    last_name,
                    group_name,
                )
        print("\tDone!\n")

    def create_user(self, username, first_name, last_name, groupname):
        print(f"\tinstalling {username}")
        contact = Contact.objects.create(
            type="P", first_name=first_name, last_name=last_name
        )
        u = User.objects.create_user(
            username=username,
            password=DEFAULT_INIT_PASS,
            contact=contact,
            first_name=first_name,
            last_name=last_name,
        )
        u.is_staff = True
        u.groups.add(Group.objects.get(name=groupname))
        u.save()

    def create_groups(self):
        print("-- Creating groups:")
        for group in self.GROUPS:
            self.create_group(group)
        print("\tDone!\n")

    def create_group(self, groupname):
        print(f"\tCreating and setting permissions for group '{groupname}'")
        group, _ = Group.objects.get_or_create(name=groupname)
        group_perms_name = groupname.upper().replace("-", "_")
        group_perms = getattr(permissions_map, group_perms_name + "_PERMS", None)
        if group_perms is None:
            return
        all_perms_codenames = []
        for perm_tuple in group_perms:
            model_name, perms = perm_tuple
            for perm in perms:
                all_perms_codenames.append(perm + "_" + model_name)
        perms = list(Permission.objects.filter(codename__in=all_perms_codenames))
        group.permissions.add(*perms)
        group.save()

    def create_superuser(self):
        print("-- installing Superuser:")
        if not User.objects.filter(username="superuser").exists():
            superuser = User.objects.create_superuser(
                username="superuser",
                password=DEFAULT_INIT_PASS,
            )
            superuser.first_name = "Application"
            superuser.last_name = "Superuser"
            superuser.is_staff = True
            superuser.groups.add(Group.objects.get_or_create(name="Admins")[0])
            superuser.save()
        print("\tDone!\n")

    def install_fixtures(self):
        # doing this to be able to call init_db form anywhere
        print("-- Installing FIXTURES:")
        fixtures_init_path = str(settings.BASE_DIR) + "/backend/"

        #
        # --------------------------------------------------------------------------------------------------
        # --------------- COMMON fixtures
        #
        print("\tInstalling Countries fixture... :", end="")
        call_command("loaddata", f"{fixtures_init_path}fixtures/common/country.json")
        # print("\tInstalling Cities fixture... :", end="")
        # call_command("loaddata", f"{fixtures_init_path}fixtures/common/city.json")
        #
        # --------------------------------------------------------------------------------------------------
        # --------------- REAL_ESTATE fixtures
        #
        print("\tInstalling Property Categories fixture... :", end="")
        call_command(
            "loaddata", f"{fixtures_init_path}fixtures/real_estate/property_category.json"
        )

        print("\tInstalling Property Category Types fixture... :", end="")
        call_command(
            "loaddata",
            f"{fixtures_init_path}fixtures/real_estate/property_category_types.json",
        )
        # --------------------------------------------------------------------------------------------------
        print("\tDone!\n")

    def init_organization(self):
        organization_name = os.getenv("ORGANIZATION_NAME")

        if not organization_name:
            raise ValueError("Organization name missing.")

        print("-- Installing Organization:")
        organization_contact, _ = Contact.objects.get_or_create(
            type=Contact.TypeChoices.COMPANY,
            name=organization_name,
        )
        organization, _ = Organization.objects.get_or_create(
            name=organization_name,
            slug=slugify(organization_name),
            contact=organization_contact,
            tax_office="",
            tax_identification_number="",
        )
        print("\tDone!\n")
        return organization

    def handle(self, *args, **options):
        with transaction.atomic():
            self.create_groups()
            self.install_fixtures()
            self.create_superuser()
            self.create_users()
