from django import forms
from django.core.exceptions import ValidationError
from . import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation


class ContactForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Ex. Name'
            }
        )
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Ex. LastName'
            }
        )
    )

    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Ex. +91 (99) 99999-99999'
            }
        )
    )

    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'name@mail.com'
            }
        ),
        label='E-mail'
    )

    picture = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        required=False
    )

    class Meta:
        model = models.Contact
        fields = (
            'first_name',
            'last_name',
            'phone',
            'email',
            'description',
            'category',
            'picture',
        )

    def clean(self):
        first_name = self.cleaned_data.get('first_name').strip()
        last_name = self.cleaned_data.get('last_name').strip()

        if first_name.lower() == last_name.lower():
            msg = ValidationError(
                'First name cannot be the same as last name',
                code='invalid'
            )
            self.add_error('last_name', msg)
            self.add_error('first_name', msg)

        return super().clean()

    def clean_first_name(self):
        cleaned_data = self.cleaned_data.get('first_name').strip()

        if cleaned_data.lower() == 'abc' or len(cleaned_data) < 3:
            self.add_error(
                'first_name',
                ValidationError(
                    'Invalid Name',
                    code='invalid'
                )
            )

        return cleaned_data

    def clean_last_name(self):
        cleaned_data = self.cleaned_data.get('last_name').strip()

        if cleaned_data.lower() == 'abc' or len(cleaned_data) < 3:
            self.add_error(
                'last_name',
                ValidationError(
                    'Invalid Name',
                    code='invalid'
                )
            )

        return cleaned_data


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        required=True,
        min_length=3
    )
    last_name = forms.CharField(
        required=True,
        min_length=3
    )
    email = forms.EmailField(
        required=True
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'username',
            'password1',
            'password2'
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            self.add_error(
                'email',
                ValidationError('Email already exists', code='invalid')
            )

        return email


class RegisterUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
        error_messages={
            'min_length': 'Please, add more than 3 letters.'
        }
    )
    last_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
    )

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )

    password2 = forms.CharField(
        label="ReEnter Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text='Use the same password as before.',
        required=False,
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'username',
        )

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        user = super().save(commit=False)
        password = cleaned_data.get('password1')

        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                self.add_error(
                    'password2',
                    ValidationError('Passwords do not match')
                )

        return super().clean()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_email = self.instance.email

        if current_email != email:
            if User.objects.filter(email=email).exists():
                self.add_error(
                    'email',
                    ValidationError('Email already exists', code='invalid')
                )

        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as errors:
                self.add_error(
                    'password1',
                    ValidationError(errors)
                )

        return password1
