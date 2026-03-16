try:
    from rest_framework_simplejwt.views import (
        TokenObtainPairView,
        TokenRefreshView,
    )
except ImportError:
    class TokenObtainPairView:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "`rest_framework_simplejwt` is not installed. "
                "Must provide alternative authentication for Admin Adapter."
            )
    class TokenRefreshView:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "`rest_framework_simplejwt` is not installed. "
                "Must provide alternative authentication for Admin Adapter."
            )

class AdminTokenObtainPairView(TokenObtainPairView):...


class AdminTokenRefreshView(TokenRefreshView): ...
