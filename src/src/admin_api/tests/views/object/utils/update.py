from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from django_admin_adapter.views.utils import (
    DATE_FIELD_STR_FORMAT,
    TIME_FIELD_STR_FORMAT,
)


def get_update_agreement_response(agreement, client, data=None, commissions_data=None):
    update_data = {
        "status": agreement.status,
        "description": "Updated description",
        "agreement_signing_date": agreement.agreement_signing_date.strftime(
            DATE_FIELD_STR_FORMAT
        )
        if agreement.agreement_signing_date
        else "",
        "signing_time": agreement.signing_time.strftime(TIME_FIELD_STR_FORMAT)
        if agreement.signing_time
        else "",
        "assigned_to": agreement.assigned_to_id or "",
        "project": agreement.project_id or "",
        "property": agreement.property_id or "",
        "unique_id": agreement.unique_id or "",
        "website_url": agreement.website_url or "",
        "slug": agreement.slug or "",
        "closure_percentage": agreement.closure_percentage or "",
        "agreement_int": agreement.agreement_int or "",
        "valid_from": agreement.valid_from.strftime(DATE_FIELD_STR_FORMAT)
        if agreement.valid_from
        else "",
        "valid_until": agreement.valid_until.strftime(DATE_FIELD_STR_FORMAT)
        if agreement.valid_until
        else "",
        "cancel_date": agreement.cancel_date.strftime(DATE_FIELD_STR_FORMAT)
        if agreement.cancel_date
        else "",
        "reservation_date": agreement.reservation_date.strftime(DATE_FIELD_STR_FORMAT)
        if agreement.reservation_date
        else "",
        "price": agreement.price or "",
        "down_payment": agreement.down_payment or "",
        "private_agreement_date": agreement.private_agreement_date.strftime(
            DATE_FIELD_STR_FORMAT
        )
        if agreement.private_agreement_date
        else "",
    }

    update_data.update(data or {})
    update_data.update(commissions_data or {})

    return client.put(
        f"/api/real_estate/agreement/{agreement.pk}/",
        data=encode_multipart(
            data=update_data,
            boundary=BOUNDARY,
        ),
        content_type=MULTIPART_CONTENT,
    )
