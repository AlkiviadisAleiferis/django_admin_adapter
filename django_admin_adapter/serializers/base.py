from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers


class BaseAdminSerializer(serializers.ModelSerializer):
    """
    ModelSerializer that pre-sets specific attrs

    enables:
        - dynamic `Meta` definition of model/fields
        - passing `ModelAdmin` to fields
        - specifying model/admin fields

    sets on serializer:
        - `self.Meta.model`
        - `self.Meta.fields`
        - `self.admin_calc_fields`

    Used by both the `AdminListSerializer`
    and `AdminObjectViewSerializer` serializers.
    """

    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model_class")
        given_fields = kwargs.pop("all_fields")
        ignore_pk = kwargs.pop("ignore_pk", False)

        model_admin = kwargs["context"]["model_admin"]

        model_meta_fields = {f.name for f in model._meta.fields}
        model_fields = []
        admin_calc_fields = []

        for fieldname in given_fields:
            if fieldname in model_meta_fields or hasattr(model, fieldname):
                model_fields.append(fieldname)
            elif hasattr(model_admin, fieldname):
                admin_calc_fields.append(fieldname)
            else:
                raise ImproperlyConfigured(
                    f"Invalid field given for Model Admin '{model_admin.__class__.__name__}': {fieldname}"
                )

        if "pk" not in given_fields and not ignore_pk:
            model_fields.append("pk")

        self.Meta.model = model
        self.Meta.fields = model_fields
        self.admin_calc_fields = admin_calc_fields

        super().__init__(*args, **kwargs)
