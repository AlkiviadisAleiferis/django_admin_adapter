from django.db import models
from rest_framework.fields import (  # NOQA # isort:skip
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    DurationField,
    EmailField,
    FileField,
    FilePathField,
    FloatField,
    IPAddressField,
    ImageField,
    IntegerField,
    ModelField,
    SlugField,
    TimeField,
    URLField,
    UUIDField,
)
from .base import BaseAdminSerializer

from .fields import (
    AdminListChoiceField,
    AdminListRelatedField,
    AdminListMethodField,
)


class AdminListSerializer(BaseAdminSerializer):
    serializer_choice_field = AdminListChoiceField
    serializer_related_field = AdminListRelatedField

    class Meta:
        pass

    def get_fields(self):
        fields = super().get_fields()
        # use `AdminListMethodField` for all admin method fields
        for fieldname in self.admin_calc_fields:
            fields[fieldname] = AdminListMethodField(
                self.instance, self.context["model_admin"], method_name=fieldname
            )
        return fields
