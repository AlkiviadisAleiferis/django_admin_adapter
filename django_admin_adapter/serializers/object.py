from django.db import models
from django.contrib import admin
from rest_framework.compat import postgres_fields
from rest_framework.fields import (  # NOQA # isort:skip
    IPAddressField,
    HStoreField,
)
from rest_framework.relations import RelatedField
from .base import BaseAdminSerializer

from .fields import (
    #
    AdminObjectChoiceField,
    AdminObjectRelatedField,
    AdminObjectBooleanField,
    AdminObjectCharField,
    AdminObjectTextField,
    AdminObjectDateField,
    AdminObjectDateTimeField,
    AdminObjectDecimalField,
    AdminObjectDurationField,
    AdminObjectEmailField,
    AdminObjectFileField,
    AdminObjectFilePathField,
    AdminObjectFloatField,
    # IPAddressField,
    AdminObjectImageField,
    AdminObjectIntegerField,
    # ModelField,
    AdminObjectModelField,
    AdminObjectSlugField,
    AdminObjectTimeField,
    AdminObjectURLField,
    AdminObjectUUIDField,
    # HStoreField,
    AdminObjectListField,
    AdminObjectJSONField,
    #
    AdminListMethodField,
    AdminObjectViewMethodField,
    AdminObjectManyRelatedField,
)


OBJECT_PREVIEW_SERIALIZER_FIELD_MAPPING = {
    models.DateTimeField: AdminObjectDateTimeField,
    models.DateField: AdminObjectDateField,
    models.AutoField: AdminObjectIntegerField,
    models.BigIntegerField: AdminObjectIntegerField,
    models.BooleanField: AdminObjectBooleanField,
    models.CharField: AdminObjectCharField,
    models.CommaSeparatedIntegerField: AdminObjectCharField,
    models.DecimalField: AdminObjectDecimalField,
    models.DurationField: AdminObjectDurationField,
    models.EmailField: AdminObjectEmailField,
    models.Field: AdminObjectModelField,
    models.FileField: AdminObjectFileField,
    models.FloatField: AdminObjectFloatField,
    models.ImageField: AdminObjectImageField,
    models.IntegerField: AdminObjectIntegerField,
    models.NullBooleanField: AdminObjectBooleanField,
    models.PositiveIntegerField: AdminObjectIntegerField,
    models.PositiveSmallIntegerField: AdminObjectIntegerField,
    models.SlugField: AdminObjectSlugField,
    models.SmallIntegerField: AdminObjectIntegerField,
    models.TextField: AdminObjectTextField,
    models.TimeField: AdminObjectTimeField,
    models.URLField: AdminObjectURLField,
    models.UUIDField: AdminObjectUUIDField,
    models.GenericIPAddressField: IPAddressField,
    models.FilePathField: AdminObjectFilePathField,
}


class AdminObjectViewSerializer(BaseAdminSerializer):
    serializer_field_mapping = OBJECT_PREVIEW_SERIALIZER_FIELD_MAPPING
    serializer_choice_field = AdminObjectChoiceField
    serializer_related_field = AdminObjectRelatedField
    if hasattr(models, "JSONField"):
        serializer_field_mapping[models.JSONField] = AdminObjectJSONField
    if postgres_fields:
        serializer_field_mapping[postgres_fields.HStoreField] = HStoreField
        serializer_field_mapping[postgres_fields.ArrayField] = AdminObjectListField
        serializer_field_mapping[postgres_fields.JSONField] = AdminObjectJSONField

    class Meta:
        pass

    def get_fields(self):
        fields = super().get_fields()

        for fieldname in fields:
            # set `model_admin` on field instance to use in repr
            # set `_admin_site` on field instance to use in related objects
            # set `_view_request` on field instance to use in related objects
            fields[fieldname].model_admin = self.context.get("model_admin")
            fields[fieldname].serializer_model = self.Meta.model
            fields[fieldname]._view_request = self.context["request"]
            fields[fieldname]._admin_site = self.context["admin_site"]

            if isinstance(fields[fieldname], AdminObjectManyRelatedField):
                fields[fieldname].child_relation.model_admin = self.context.get("model_admin")
                fields[fieldname].child_relation.serializer_model = self.Meta.model

        # use `AdminObjectViewMethodField` for all admin method fields
        for fieldname in self.admin_calc_fields:
            fields[fieldname] = AdminObjectViewMethodField(
                self.instance, self.context["model_admin"], method_name=fieldname
            )

        return fields

    def to_representation(self, instance):
        model_meta = self.Meta.model._meta
        model_fields = {f.name for f in model_meta.fields}

        rep = super().to_representation(instance)

        for fieldname in rep:
            if fieldname in model_fields:
                if rep[fieldname] is None:
                    field = self.fields[fieldname]

                    # we deal specifically with RelatedField here
                    # to avoid errors on representation
                    # also get all the permissions of the related model
                    if isinstance(field, RelatedField):
                        source_field = self.Meta.model._meta.get_field(fieldname)
                        remote_model = source_field.remote_field.model
                        remote_model_admin = self.context["admin_site"]._registry.get(
                            remote_model
                        )
                        request = self.context["request"]
                        if remote_model_admin is None:
                            permissions = {
                                "view": False,
                                "add": False,
                                "change": False,
                                "delete": False,
                            }
                        else:
                            permissions = {
                                "view": remote_model_admin.has_view_permission(request, None),
                                "add": remote_model_admin.has_add_permission(request),
                                "change": remote_model_admin.has_change_permission(
                                    request, None
                                ),
                                "delete": remote_model_admin.has_delete_permission(
                                    request, None
                                ),
                            }

                        rep[fieldname] = {
                            "type": "RelatedField",
                            "pk": None,
                            "app": remote_model._meta.app_label,
                            "model": remote_model._meta.model_name,
                            "value": None,
                            "help_text": "",
                            "permissions": permissions,
                        }
                    else:
                        rep[fieldname] = field.to_representation(None)

            # model admin calc fields
            else:
                if rep[fieldname] is None:
                    rep[fieldname] = self.fields[fieldname].to_representation(None)

        return rep
