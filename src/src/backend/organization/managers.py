from django.contrib.auth.base_user import BaseUserManager

from backend.common.models import Contact


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password=None, **extra_fields):
        """
        Creates and saves a User with the given username and password.
        """
        if not username:
            raise ValueError("The username must be given")
        if password is None:
            raise ValueError("No password provided")

        username = self.normalize_email(username)
        user = self.model(username=self.normalize_email(username), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **kwargs):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        if password is None:
            raise ValueError("No password provided")
        user = self.create_user(username, password=password)
        user.is_superuser = True
        user.save(using=self._db)
        return user
