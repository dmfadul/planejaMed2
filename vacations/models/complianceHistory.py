from django.db import models
from core.models import User
from shifts.models import Month


class ComplianceHistory(models.Model):
    class ComplianceStatus(models.TextChoices):
        COMPLIANT = "C", "Compliant"
        NONCOMPLIANT = "N", "Non-compliant"
        UNKNOWN = "U", "Unknown"   # optional
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compliance_history')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='compliance_histories')
    status = models.CharField(max_length=1, choices=ComplianceStatus.choices, default=ComplianceStatus.UNKNOWN)

    # Auditability fields
    rule_version = models.CharField(max_length=20, null=True, blank=True)
    reason = models.JSONField(default=dict, blank=True)  # details about non-compliance
    source = models.CharField(max_length=10, default='system')  # e.g., 'system', 'manual'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'month'], name='unique_user_month')
        ]

        indexes = [
            models.Index(fields=['user', 'month']),
        ]

    # add method to get user 'uptodate' with his compliance status
    # add method to test for eligibility based on last 6 months
    