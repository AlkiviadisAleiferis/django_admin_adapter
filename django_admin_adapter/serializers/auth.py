try:
    from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
except ImportError:
    class TokenObtainPairSerializer:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "`rest_framework_simplejwt` is not installed. "
                "Must provide alternative authentication for Admin Adapter."
            )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = getattr(user, user.USERNAME_FIELD, None)
        token["identifier"] = str(user)
        return token
