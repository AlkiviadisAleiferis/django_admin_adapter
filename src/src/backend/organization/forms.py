from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    AuthenticationForm,
    ReadOnlyPasswordHashField,
)
from django.core.exceptions import ValidationError

from backend.common.models import Contact

from .models import User


class UserLoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "email or password are invalid",
        "inactive": "This account is inactive",
    }


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(
        label="Confirm password", widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "contact")

    def clean(self):
        if (
            self.cleaned_data.get("first_name") is None
            or self.cleaned_data.get("last_name") is None
        ):
            raise ValidationError("User first and last name must be provided")

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if not password1 or not password2:
            raise ValidationError("Please provide both passwords")
        if password1 != password2:
            raise ValidationError("The provided passwords don't match")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "is_active",
            "first_name",
            "last_name",
        )
