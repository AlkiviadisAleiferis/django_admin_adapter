import jwt

from django.conf import settings
from django_admin_adapter.viewmap import VIEWMAP
from rest_framework import status
from rest_framework.test import APIClient
from ...conftest import DEFAULT_PASSWORD


def test_authentication_failure_wrong_password(staff_client):
    data = {"username": staff_client.user.username, "password": "wrong"}
    client = APIClient()
    response = client.post("/api/" + VIEWMAP["token_obtain_pair"][0], data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authentication_failure_wrong_username():
    data = {"username": "wrong", "password": "wrong"}
    client = APIClient()
    response = client.post("/api/" + VIEWMAP["token_obtain_pair"][0], data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authentication_success(staff_client):
    data = {"username": staff_client.user.username, "password": DEFAULT_PASSWORD}
    client = APIClient()
    response = client.post("/api/" + VIEWMAP["token_obtain_pair"][0], data)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert "access" in response.data
    assert "refresh" in response.data


def test_authentication_refresh_failure(staff_client):
    response = staff_client.post("/api/" + VIEWMAP["token_refresh"][0])
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_authentication_refresh_success(staff_client):
    data = {"username": staff_client.user.username, "password": DEFAULT_PASSWORD}
    client = APIClient()
    response = client.post("/api/" + VIEWMAP["token_obtain_pair"][0], data)

    refresh_token = response.data["refresh"]
    response = client.post(
        "/api/" + VIEWMAP["token_refresh"][0], {"refresh": refresh_token}
    )

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.data["access"]


def test_decoded_access_token_extra_fields(staff_client):
    response = staff_client.post(
        "/api/token/",
        data={"username": staff_client.user.username, "password": DEFAULT_PASSWORD},
    )
    assert response.status_code == 200
    token = response.data["access"]
    decoded_token = jwt.decode(token, settings.SECRET_KEY, ["HS256"])
    assert decoded_token["identifier"] == "Chumbius Kius"
    assert decoded_token["username"] == "pilot"
    assert decoded_token["user_id"] == staff_client.user.id
