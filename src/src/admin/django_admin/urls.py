from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import (  # noqa: F401
    local_media_access,  # noqa: F401
)


urlpatterns = [
    path("", admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = (
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        + [path("djangodebugtoolbarlol/", include(debug_toolbar.urls))]
        + urlpatterns
    )
