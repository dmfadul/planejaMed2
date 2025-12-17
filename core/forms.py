from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': (
            "Por favor, insira um CRM e uma senha corretos."
        ),
        'inactive': ("Esta conta está inativa."),
    }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "rqe", "email", "phone"]  # pick what you want editable
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "rqe": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise ValidationError("Name is required.")
        # keep the same normalization you use in create_user
        return " ".join([n.capitalize() for n in name.split()])

    def clean_email(self):
        # your model default is test@example.com, so users might forget to update it
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise ValidationError("Email is required for password recovery.")
        return email
