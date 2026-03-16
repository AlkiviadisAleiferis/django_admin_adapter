import pytest
from django.core.management import call_command
from rest_framework.test import APIRequestFactory

from rest_framework.test import APIClient

from backend.tests import factories


DEFAULT_NON_STAFF_USERNAME = "pilot1"
DEFAULT_NO_PERMS_USERNAME = "pilot2"

# created at session start from init_db
# has
DEFAULT_WITH_PERMS_USERNAME = "pilot"
SUPERUSER_USERNAME = "superuser"  # created at session start from init_db

DEFAULT_PASSWORD = "1234"


@pytest.fixture
def settings_no_tz(settings):
    # if USE_TZ == True,
    # the DateTime fields are timezone-aware
    # not UTC
    settings.USE_TZ = False


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("init_db")


@pytest.fixture(scope="session")
def non_staff_client(django_db_setup, django_db_blocker):
    api_client = APIClient()
    username, password = DEFAULT_NON_STAFF_USERNAME, DEFAULT_PASSWORD

    with django_db_blocker.unblock():
        user = factories.UserFactory.create(
            username=username, password=password, is_staff=False
        )
        api_client.user = user
        response = api_client.post(
            "/api/token/", data={"username": username, "password": password}
        )
        assert response.status_code == 200
        api_client.credentials(
            HTTP_AUTHORIZATION="Bearer {}".format(response.data["access"])
        )

    return api_client


@pytest.fixture(scope="session")
def no_perms_staff_client(django_db_setup, django_db_blocker):
    api_client = APIClient()
    username, password = DEFAULT_NO_PERMS_USERNAME, DEFAULT_PASSWORD

    with django_db_blocker.unblock():
        user = factories.UserFactory.create(
            username=username, password=password, is_staff=True
        )
        api_client.user = user
        response = api_client.post(
            "/api/token/", data={"username": username, "password": password}
        )
        assert response.status_code == 200
        api_client.credentials(
            HTTP_AUTHORIZATION="Bearer {}".format(response.data["access"])
        )

    return api_client


@pytest.fixture(scope="session")
def staff_client(django_db_setup, django_db_blocker):
    api_client = APIClient()
    username, password = DEFAULT_WITH_PERMS_USERNAME, DEFAULT_PASSWORD

    with django_db_blocker.unblock():
        user = factories.UserFactory.create(
            username=username, password=password, is_staff=True
        )
        api_client.user = user
        response = api_client.post(
            "/api/token/", data={"username": username, "password": password}
        )
        assert response.status_code == 200
        api_client.credentials(
            HTTP_AUTHORIZATION="Bearer {}".format(response.data["access"])
        )

    return api_client


@pytest.fixture(scope="session")
def superuser_client(django_db_setup, django_db_blocker):
    api_client = APIClient()
    username, password = SUPERUSER_USERNAME, DEFAULT_PASSWORD

    with django_db_blocker.unblock():
        user = factories.UserFactory.create(
            username=username,
            password=password,
            is_staff=True,
            is_superuser=True,
        )
        api_client.user = user
        response = api_client.post(
            "/api/token/", data={"username": username, "password": password}
        )
        assert response.status_code == 200
        api_client.credentials(
            HTTP_AUTHORIZATION="Bearer {}".format(response.data["access"])
        )

    return api_client


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def api_rf(staff_client):
    rf = APIRequestFactory()
    return rf
