# forms.py
from django import forms
from .models import UploadedDocument


class UploadedDocumentForm(forms.ModelForm):
    class Meta:
        model = UploadedDocument
        fields = ["file_type", "file"]

    def clean_file(self):
        f = self.cleaned_data["file"]
        allowed_extensions = [".xlsx"]
        name = f.name.lower()

        if not any(name.endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError("Apenas arquivos .xlsx são permitidos.")

        return f