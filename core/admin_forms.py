from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("crm", "name", "email", "alias", "phone", "rqe")

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        return " ".join([n.capitalize() for n in name.split()])

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    # This makes password read-only hash + enables the “change password” flow
    password = ReadOnlyPasswordHashField(label="Password")

    class Meta:
        model = User
        fields = (
            "crm", "password", "name", "alias", "email", "phone", "rqe",
            "is_active", "is_staff", "is_superuser", "is_manager",
            "groups", "user_permissions",
        )
