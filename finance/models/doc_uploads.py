# models.py
import os
import uuid
from django.db import models


def upload_document_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or ".bin"
    return (
        f"documents/"
        f"month_{instance.month_id}/"
        f"{instance.file_type}/"
        f"{uuid.uuid4()}{ext}"
    )


class UploadedDocument(models.Model):
    FILE_TYPE_CHOICES = [
        ("synthetic", "Synthetic"),
        ("detailed", "Detailed"),
    ]

    month = models.ForeignKey(
        "shifts.Month",
        on_delete=models.CASCADE,
        related_name="uploaded_documents",
    )
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    file = models.FileField(upload_to=upload_document_path)
    original_name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file_type} - month {self.month_id}"