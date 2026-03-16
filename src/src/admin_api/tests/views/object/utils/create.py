from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import encode_multipart, BOUNDARY, MULTIPART_CONTENT

from backend.real_estate.models import Agreement


DATE_FIELD_STR_FORMAT = "%Y-%m-%d"
TIME_FIELD_STR_FORMAT = "%H:%M:%S"


def get_create_agreement_response(client, data=None, commissions_data=None):
    """
    Utility function to create an agreement via POST request.

    Args:
        client: The test client to use for the request
        data: Optional dict of data to override defaults
        commissions_data: Optional dict of inline formset data for commissions

    Returns:
        Response object from the POST request
    """
    create_data = {
        "type": Agreement.TypeChoices.CONTRACT_OF_SALE,  # Required field
        "status": Agreement.StatusChoices.OPEN,  # Required field
        "description": "Test agreement description",
        "agreement_signing_date": "",
        "signing_time": "",
        "assigned_to": "",
        "project": "",
        "property": "",
        "unique_id": "",
        "website_url": "",
        "slug": "",
        "closure_percentage": "",
        "agreement_int": "",
        "valid_from": "",
        "valid_until": "",
        "cancel_date": "",
        "reservation_date": "",
        "price": "",
        "down_payment": "",
        "private_agreement_date": "",
    }

    # Add default inline formset management data if not provided
    if commissions_data is None and client.user.has_perm(
        "real_estate.add_agreementcommission"
    ):
        commissions_data = {
            "commissions-TOTAL_FORMS": "1",
            "commissions-INITIAL_FORMS": "0",
            "commissions-MIN_NUM_FORMS": "0",
            "commissions-MAX_NUM_FORMS": "0",
        }

    create_data.update(data or {})
    create_data.update(commissions_data or {})

    return client.post(
        "/api/real_estate/agreement/",
        data=encode_multipart(
            data=create_data,
            boundary=BOUNDARY,
        ),
        content_type=MULTIPART_CONTENT,
    )
