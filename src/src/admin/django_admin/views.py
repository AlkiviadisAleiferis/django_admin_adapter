import logging
from django.http import (
    HttpResponse,
)


logger = logging.getLogger()


def local_media_access(request, model_name, pk, filename):
    response = HttpResponse()
    # Content-type will be detected by nginx
    del response["Content-Type"]
    response["X-Accel-Redirect"] = "/serve-media/" + f"{model_name}/{pk}/{filename}"
    return response
