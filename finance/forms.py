# forms.py
from django import forms
from .models import UploadedDocument


class UploadedDocumentForm(forms.ModelForm):
    class Meta:
        model = UploadedDocument
        fields = ["file_type", "file"]

    def clean_file(self):
        f = self.cleaned_data["file"]
        allowed_extensions = [".pdf", ".xlsx", ".xls"]
        name = f.name.lower()

        if not any(name.endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError("Only PDF and spreadsheet files are allowed.")

        return f