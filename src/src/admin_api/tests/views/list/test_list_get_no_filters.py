import pytest
from datetime import timezone, datetime
from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.admin.views.main import PAGE_VAR, ORDER_VAR
from rest_framework import status

from admin_api.model_admins import AgreementAdmin
from backend.tests.factories import AgreementFactory
from backend.real_estate.models import Agreement
from backend.organization.models import User
from .utils import get_serialized_agreement_data


@pytest.fixture
def agreement_admin():
    agreement_admin = admin.site._registry[Agreement]
    initial_list_per_page = agreement_admin.list_per_page
    initial_list_max_show_all = agreement_admin.list_max_show_all
    initial_list_display = agreement_admin.list_display
    agreement_admin.list_per_page = 2
    agreement_admin.list_max_show_all = 3
    agreement_admin.ordering = ("-id",)

    yield agreement_admin

    agreement_admin.list_per_page = initial_list_per_page
    agreement_admin.list_max_show_all = initial_list_max_show_all
    agreement_admin.list_display = initial_list_display


def test_list_only_get_and_post_allowed(staff_client):
    for method in ["put", "patch", "delete"]:
        resp = getattr(staff_client, method)("/api/real_estate/agreement/")
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_list_base_permission_check(non_staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    resp = non_staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    admin_site_has_permission_spy.assert_called()


def test_list_base_admin_apiview_errors(staff_client):
    # Non-existent app
    resp = staff_client.get("/api/notanapp/agreement/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Non-existent model (real_estate app exists)
    resp = staff_client.get("/api/real_estate/notamodel/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (1)."}

    # Model exists but no admin registered
    resp = staff_client.get("/api/common/country/")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"detail": "Invalid URL params (2)."}


def test_list_view_or_change_permission_only(db, no_perms_staff_client):
    view_perm = Permission.objects.get(codename="view_agreement")
    change_perm = Permission.objects.get(codename="change_agreement")

    # No permission
    resp = no_perms_staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # Only view permission
    no_perms_staff_client.user.user_permissions.set([view_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_200_OK

    # Only change permission
    no_perms_staff_client.user.user_permissions.set([change_perm])
    # reload user
    # to reload permissions cache
    no_perms_staff_client.user = User.objects.get(
        username=no_perms_staff_client.user.username,
    )

    resp = no_perms_staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_200_OK


def test_list_incorrect_lookup_parameters(db, staff_client):
    resp = staff_client.get("/api/real_estate/agreement/?invalid__lookup=bad")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["Incorrect GET parameters."]}


def test_list_empty_list(db, staff_client):
    resp = staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {
        "results": [],
        "page": 1,
        "total_pages": 1,
        "total_objects_num": 0,
    }


def test_list_single_object(db, staff_client, settings_no_tz):
    agreement = AgreementFactory.create()
    resp = staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {
        "results": [
            {
                "id": agreement.id,
                "status": agreement.get_status_display(),
                "type": agreement.get_type_display(),
                "created_at": agreement.created_at.strftime("%d/%m/%Y - %H:%M"),
                "updated_at": agreement.updated_at.strftime("%d/%m/%Y - %H:%M"),
                "reservation_date": agreement.reservation_date.strftime("%d/%m/%Y")
                if agreement.reservation_date
                else None,
                "assigned_to": str(agreement.assigned_to)
                if agreement.assigned_to
                else None,
                "project": str(agreement.project) if agreement.project else None,
                "property": str(agreement.property) if agreement.property else None,
                "valid_from": agreement.valid_from.strftime("%d/%m/%Y")
                if agreement.valid_from
                else None,
                "valid_until": agreement.valid_until.strftime("%d/%m/%Y")
                if agreement.valid_until
                else None,
                "cancel_date": agreement.cancel_date.strftime("%d/%m/%Y")
                if agreement.cancel_date
                else None,
                "pk": agreement.pk,
            }
        ],
        "page": 1,
        "total_pages": 1,
        "total_objects_num": 1,
    }


def test_list_multiple_objects(db, staff_client, settings_no_tz):
    AgreementFactory.create_batch(5)
    # default ordering is the -id
    agreements = Agreement.objects.all().order_by("-id")
    results = [get_serialized_agreement_data(a) for a in agreements]
    resp = staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {
        "results": results,
        "page": 1,
        "total_pages": 1,
        "total_objects_num": 5,
    }


def test_list_list_display_fields_match_fields_in_result(db, staff_client):
    AgreementFactory.create()
    resp = staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_200_OK
    result_fields = set(resp.data["results"][0])
    expected_fields = set(
        admin.site._registry[Agreement].get_list_display("dummy_request") + ("pk",)
    )
    assert result_fields == expected_fields


# Pagination Tests


def test_list_pagination_first_page(db, staff_client, agreement_admin):
    # Create more objects than list_per_page (20)
    AgreementFactory.create_batch(3)
    resp = staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["results"]) == 2  # list_per_page
    assert resp.data["total_objects_num"] == 3
    assert resp.data["total_pages"] == 2
    assert resp.data["page"] == 1


def test_list_pagination_second_page(db, staff_client, agreement_admin):
    AgreementFactory.create_batch(3)
    resp = staff_client.get(f"/api/real_estate/agreement/?{PAGE_VAR}=2")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["results"]) == 1  # Remaining objects
    assert resp.data["total_objects_num"] == 3
    assert resp.data["total_pages"] == 2
    assert resp.data["page"] == 2


def test_list_pagination_exact_page_size(db, staff_client, agreement_admin):
    AgreementFactory.create_batch(2)
    resp = staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["results"]) == 2
    assert resp.data["total_objects_num"] == 2
    assert resp.data["total_pages"] == 1
    assert resp.data["page"] == 1


def test_list_pagination_multiple_pages(db, staff_client, agreement_admin):
    AgreementFactory.create_batch(5)

    resp = staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["total_pages"] == 3  # 5 / 2 = 2.5, rounded up to 3
    assert resp.data["total_objects_num"] == 5
    assert resp.data["page"] == 1

    resp = staff_client.get(f"/api/real_estate/agreement/?{PAGE_VAR}=3")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["total_pages"] == 3  # 5 / 2 = 2.5, rounded up to 3
    assert resp.data["total_objects_num"] == 5
    assert resp.data["page"] == 3


def test_list_pagination_invalid_page(db, staff_client, agreement_admin):
    AgreementFactory.create_batch(5)
    # Page 10 doesn't exist
    resp = staff_client.get(f"/api/real_estate/agreement/?{PAGE_VAR}=10")
    # Django's paginator should handle this gracefully
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["Incorrect GET parameters."]}


# Sorting Tests


def test_list_sort_by_valid_from_ascending(db, staff_client, settings_no_tz):
    AgreementFactory.create_batch(3)

    agreements = Agreement.objects.all().order_by("valid_from", "-id")
    results = [get_serialized_agreement_data(a) for a in agreements]
    resp = staff_client.get(f"/api/real_estate/agreement/?{ORDER_VAR}=11")

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["results"]) == 3
    assert resp.data["results"] == results


def test_list_sort_by_valid_from_descending(db, staff_client, settings_no_tz):
    AgreementFactory.create_batch(3)

    agreements = Agreement.objects.all().order_by("-valid_from", "-id")
    results = [get_serialized_agreement_data(a) for a in agreements]
    resp = staff_client.get(f"/api/real_estate/agreement/?{ORDER_VAR}=-11")

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["results"]) == 3
    assert resp.data["results"] == results


def test_list_ordering_respects_field_ordering_priority(
    db, staff_client, settings_no_tz, agreement_admin
):
    AgreementFactory.create(
        valid_from=datetime.now().date() + relativedelta(days=10),
        reservation_date=datetime.now().date() + relativedelta(days=-10),
    )
    AgreementFactory.create(
        valid_from=datetime.now().date() + relativedelta(days=-10),
        reservation_date=datetime.now().date() + relativedelta(days=10),
    )

    agreements = Agreement.objects.all().order_by("valid_from", "reservation_date", "-id")
    results = [get_serialized_agreement_data(a) for a in agreements]
    resp = staff_client.get(f"/api/real_estate/agreement/?{ORDER_VAR}=11.6")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["results"] == results

    # now change the order of the ordered fields
    agreements = Agreement.objects.all().order_by("reservation_date", "valid_from", "-id")
    results = [get_serialized_agreement_data(a) for a in agreements]
    resp = staff_client.get(f"/api/real_estate/agreement/?{ORDER_VAR}=6.11")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["results"] == results


def test_list_sort_by_non_sortable_field(db, staff_client):
    AgreementFactory.create_batch(3)
    # Try to sort by field not in sortable_by (e.g., status is position 2)
    resp = staff_client.get(f"/api/real_estate/agreement/?{ORDER_VAR}=2")
    # Should return 400 because 'status' is not in sortable_by
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["Invalid sorting field(s)."]}


def test_list_sort_by_multiple_fields(db, staff_client, settings_no_tz):
    AgreementFactory.create_batch(5)
    agreements = Agreement.objects.all().order_by("valid_from", "created_at", "-id")
    results = [get_serialized_agreement_data(a) for a in agreements]
    resp = staff_client.get(f"/api/real_estate/agreement/?{ORDER_VAR}=11.4")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["results"]) == 5
    assert resp.data["results"] == results


def test_list_sort_invalid_field_number(db, staff_client):
    AgreementFactory.create_batch(3)
    # Field number 999 doesn't exist
    resp = staff_client.get(f"/api/real_estate/agreement/?{ORDER_VAR}=999")
    # Should return 400 because field number doesn't exist in list_display
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"messages": ["Invalid sorting field(s)."]}


def test_list_sort_with_pagination(db, staff_client, settings_no_tz, agreement_admin):
    AgreementFactory.create_batch(3)
    agreements = Agreement.objects.all().order_by("valid_from", "-id")
    results = [get_serialized_agreement_data(a) for a in agreements][:2]

    resp = staff_client.get(f"/api/real_estate/agreement/?{ORDER_VAR}=11&{PAGE_VAR}=1")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["results"]) == 2
    assert resp.data["page"] == 1
    assert resp.data["results"] == results


# Show All Results Tests


def test_list_show_all_results(db, staff_client, agreement_admin):
    # Create more than list_max_show_all objects
    AgreementFactory.create_batch(3)
    resp = staff_client.get("/api/real_estate/agreement/?all=1")
    assert resp.status_code == status.HTTP_200_OK
    # Should show all results on one page
    assert len(resp.data["results"]) == 3
    assert resp.data["total_objects_num"] == 3


def test_list_show_all_with_more_records_than_limit(db, staff_client, agreement_admin):
    # AgreementAdmin has list_max_show_all, if it's set
    # Create more objects than the limit
    AgreementFactory.create_batch(4)
    resp = staff_client.get("/api/real_estate/agreement/?all=1")
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["results"]) == 2
    assert resp.data["total_objects_num"] == 4
    assert resp.data["page"] == 1


# Integration Tests


def test_list_all_proper_methods_called(db, staff_client, mocker):
    admin_site_has_permission_spy = mocker.spy(admin.site, "has_permission")
    agreement_has_view_or_change_permission_spy = mocker.spy(
        AgreementAdmin, "has_view_or_change_permission"
    )
    agreement_get_changelist_spy = mocker.spy(AgreementAdmin, "get_changelist_instance")
    agreement_get_list_display_spy = mocker.spy(AgreementAdmin, "get_list_display")
    agreement_get_sortable_by_spy = mocker.spy(AgreementAdmin, "get_sortable_by")

    AgreementFactory.create_batch(3)
    resp = staff_client.get("/api/real_estate/agreement/")
    assert resp.status_code == status.HTTP_200_OK

    admin_site_has_permission_spy.assert_called()
    agreement_has_view_or_change_permission_spy.assert_called()
    agreement_get_changelist_spy.assert_called()
    agreement_get_list_display_spy.assert_called()
    agreement_get_sortable_by_spy.assert_called()


def test_list_concurrent_requests_same_results(db, staff_client):
    AgreementFactory.create_batch(3)
    resp1 = staff_client.get("/api/real_estate/agreement/?p=1")
    resp2 = staff_client.get("/api/real_estate/agreement/?p=1")
    assert resp1.status_code == status.HTTP_200_OK
    assert resp2.status_code == status.HTTP_200_OK
    assert resp1.data == resp2.data


def test_list_sortable_by_validation(db, staff_client, settings_no_tz):
    AgreementFactory.create_batch(10)
    agreements = Agreement.objects.all().order_by("-valid_from", "-id")
    results = [get_serialized_agreement_data(a) for a in agreements]

    resp = staff_client.get(f"/api/real_estate/agreement/?{ORDER_VAR}=-11..")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["results"] == results
