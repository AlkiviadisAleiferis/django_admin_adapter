from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import Group, PermissionsMixin
from django.db import models

from backend.common.models import (
    TimeStampedModel,
    DocumentModel,
    ImageModel,
    NameSlugModel,
)
from .managers import UserManager


# % --------------  User  -----------------


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, ImageModel):
    username = models.CharField(max_length=50, unique=True, blank=False)

    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(null=True, blank=True, max_length=50)
    last_name = models.CharField(null=True, blank=True, max_length=50)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    notifications = models.JSONField(blank=True, default=list)

    contact = models.OneToOneField(
        "common.Contact", null=True, blank=True, on_delete=models.PROTECT
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user"

    def __str__(self):
        if self.first_name is not None and self.last_name is not None:
            return f"{self.first_name} {self.last_name}"
        else:
            return f"{self.username}"

    def infosystem_upload_to(self, filename):
        return f"user/{self.pk}/{filename}"

    @property
    def is_admin_or_management(self):
        # cache result in private attr `_is_admin_or_management`
        # cache exists in the lifetime of the User instance
        if hasattr(self, "_is_admin_or_management"):
            return self._is_admin_or_management
        else:
            self._is_admin_or_management = self.groups.filter(
                name__in=("Management", "Admins")
            ).exists()
            return self._is_admin_or_management


# % ----------------------------------------------------
# % --------------  COMPANY STRUCTURE  -----------------
# % ----------------------------------------------------


class Organization(NameSlugModel):
    contact = models.OneToOneField("common.Contact", on_delete=models.PROTECT)

    objects = models.Manager()

    class Meta:
        db_table = "organization"

    def __str__(self):
        return f"{self.name}"
