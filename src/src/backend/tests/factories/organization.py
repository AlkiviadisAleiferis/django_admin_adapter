import factory
import random
import uuid

from backend.organization.models import User, Organization
from django.contrib.auth.models import Group
from backend.common.models import Contact


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"username__{uuid.uuid1()}")
    password = factory.PostGenerationMethodCall("set_password", "1234")

    first_name = factory.Sequence(lambda n: f"first_name__{uuid.uuid1()}")
    last_name = factory.Sequence(lambda n: f"last_name__{uuid.uuid1()}")
    email = factory.Sequence(lambda n: f"email_{uuid.uuid1()}@pytest.com")
    contact = factory.SubFactory("backend.tests.factories.ContactFactory")

    is_active = True
    is_staff = True

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)
        elif kwargs.get("management"):
            self.groups.add(Group.objects.get(name="Management"))
        elif kwargs.get("sales"):
            self.groups.add(Group.objects.get(name="Sales"))


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: "Organization %d" % n)
    slug = factory.Sequence(lambda n: "organization-%d" % n)
    contact = factory.SubFactory(
        "backend.tests.factories.ContactFactory", type=Contact.TypeChoices.COMPANY
    )
