from rest_framework.compat import postgres_fields
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from rest_framework.fields import (  # NOQA # isort:skip
    Field,
    BooleanField,
    CharField,
    ChoiceField,
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
    HStoreField,
    ListField,
    JSONField,
    flatten_choices_dict,
    to_choices_dict,
)
from rest_framework.relations import RelatedField, ManyRelatedField, MANY_RELATION_KWARGS
from enum import Enum


class CustomChoiceField(ChoiceField):
    def _get_choices(self):
        return self._choices

    def _set_choices(self, choices):
        self.grouped_choices = to_choices_dict(choices)
        self._choices = flatten_choices_dict(self.grouped_choices)

        # Map the string representation of choices to the underlying value.
        # Allows us to deal with eg. integer choices while supporting either
        # integer or string input, but still get the correct datatype out.

        # fixed str(key): key mistake below
        self.choice_strings_to_values = {
            str(key.value)
            if isinstance(key, Enum) and str(key) != str(key.value)
            else str(key): self.choices[key]
            for key in self.choices
        }

    choices = property(_get_choices, _set_choices)


class BaseModelAdminMethodField(Field):
    def __init__(self, instance, model_admin, method_name, **kwargs):
        self.method_name = method_name
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        self.model_admin = model_admin
        self.instance = instance
        super().__init__(**kwargs)


class AdminListMethodField(BaseModelAdminMethodField):
    def to_representation(self, obj):
        method = getattr(self.model_admin, self.method_name)
        return method(obj)


# % ------------ Admin List Fields ------------


class AdminListChoiceField(CustomChoiceField):
    def to_representation(self, value):
        return super().to_representation(value)


class AdminListRelatedField(RelatedField):
    def __init__(self, **kwargs):
        kwargs["read_only"] = False
        super().__init__(**kwargs)

    def to_representation(self, value):
        return str(value)


# % ------------ Admin Object View Fields ------------


class BaseAdminObjectField:
    def _get_model_field_help_text(self):
        try:
            model_field = self.serializer_model._meta.get_field(self.field_name)
            return getattr(model_field, "help_text", "")
        except FieldDoesNotExist:
            return ""


class AdminObjectChoiceField(CustomChoiceField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "ChoiceField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectBooleanField(BooleanField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "BooleanField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectDecimalField(DecimalField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "DecimalField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectDurationField(DurationField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "DurationField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectEmailField(EmailField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "EmailField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectFileField(FileField, BaseAdminObjectField):
    def to_representation(self, value):
        # this field returns only the path of the
        # file in the corresponding server
        # Add server path in client field
        # if no image, returns ""
        try:
            file_url = value.url
        except ValueError:
            file_url = ""
        return {
            "type": "FileField",
            "value": file_url,
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectFilePathField(FilePathField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "FilePathField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectFloatField(FloatField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "FloatField",
            "value": float(value) if value is not None else value,
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectImageField(ImageField, BaseAdminObjectField):
    def to_representation(self, value):
        # this field returns only the path of the
        # file in the corresponding server
        # Add server path in client field
        # if no image, returns ""
        try:
            file_url = value.url
        except ValueError:
            file_url = ""
        return {
            "type": "ImageField",
            "value": file_url,
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectIntegerField(IntegerField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "IntegerField",
            "value": int(value) if value is not None else value,
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectSlugField(SlugField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "SlugField",
            "value": super().to_representation(value) if value is not None else "",
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectTimeField(TimeField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "TimeField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectURLField(URLField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "URLField",
            "value": super().to_representation(value) if value is not None else "",
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectUUIDField(UUIDField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "UUIDField",
            "value": super().to_representation(value) if value is not None else "",
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectListField(ListField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "ArrayField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectJSONField(JSONField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "JSONField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectDateTimeField(DateTimeField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "DateTimeField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectDateField(DateField, BaseAdminObjectField):
    def to_representation(self, value):
        value = super().to_representation(value)
        return {
            "type": "DateField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectCharField(CharField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "CharField",
            "value": str(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectTextField(CharField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "TextField",
            "value": str(value),
            "help_text": self._get_model_field_help_text(),
        }

class AdminObjectModelField(ModelField, BaseAdminObjectField):
    def to_representation(self, value):
        return {
            "type": "ModelField",
            "value": super().to_representation(value),
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectManyRelatedField(ManyRelatedField, BaseAdminObjectField):
    def to_representation(self, iterable):
        return {
            "type": "ManyRelatedField",
            "model": self.serializer_model._meta.model_name,
            "app": self.serializer_model._meta.app_label,
            "value": super().to_representation(iterable), # [str(obj) for obj in iterable]
            "help_text": self._get_model_field_help_text(),
        }


class AdminObjectRelatedField(RelatedField, BaseAdminObjectField):
    def __init__(self, **kwargs):
        kwargs["read_only"] = False
        super().__init__(**kwargs)

    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        This method handles creating a parent `ManyRelatedField` instance
        when the `many=True` keyword argument is passed.

        Typically you won't need to override this method.

        Note that we're over-cautious in passing most arguments to both parent
        and child classes in order to try to cover the general case. If you're
        overriding this method you'll probably want something much simpler, eg:

        @classmethod
        def many_init(cls, *args, **kwargs):
            kwargs['child'] = cls()
            return CustomManyRelatedField(*args, **kwargs)
        """
        list_kwargs = {"child_relation": cls(*args, **kwargs)}
        for key in kwargs:
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return AdminObjectManyRelatedField(**list_kwargs)

    def to_representation(self, value):
        if self.field_name:
            # m2m case: every value is an object
            # self.field_name is not set cause child field
            # is not bound
            source_field = self.serializer_model._meta.get_field(self.field_name)
            remote_model = source_field.remote_field.model
            remote_model_admin = self._admin_site._registry.get(remote_model)

            if remote_model_admin is None:
                permissions = {
                    "view": False,
                    "add": False,
                    "change": False,
                    "delete": False,
                }
            else:
                permissions = {
                    "view": remote_model_admin.has_view_permission(self._view_request, value),
                    "add": remote_model_admin.has_add_permission(self._view_request),
                    "change": remote_model_admin.has_change_permission(
                        self._view_request, value
                    ),
                    "delete": remote_model_admin.has_delete_permission(
                        self._view_request, value
                    ),
                }
        else:
            permissions = {
                "view": False,
                "add": False,
                "change": False,
                "delete": False,
            }

        return {
            "type": "RelatedField",
            "pk": value.pk if value else None,
            "model": value._meta.model_name if value else None,
            "app": value._meta.app_label if value else None,
            "value": str(value),
            "help_text": self._get_model_field_help_text(),
            "permissions": permissions,
        }


class AdminObjectViewMethodField(BaseModelAdminMethodField):
    def to_representation(self, obj):
        method = getattr(self.model_admin, self.method_name)
        return {
            "type": "MethodField",
            "value": method(obj),
            "help_text": None,
        }
