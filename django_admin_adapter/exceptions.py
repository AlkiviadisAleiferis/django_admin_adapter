from rest_framework.exceptions import APIException


class AdminAPIAdapterError(Exception):
    """
    A Generic class for raising errors
    related strictly to the Api Adapter's
    improper usage.
    """


class InvalidURLParamsError(APIException):
    status_code = 400
    default_detail = 'Invalid url parameters provided.'
    default_code = 'invalid_url_params'
