from django.db import models, transaction
from core.constants import VACATION_RULES
from core.models import User
from shifts.models import Month
from vacations.services import (
    gen_base_compliance_report,
    gen_month_compliance_report
)


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

    def _rule_version_for(user):
        return "old_policy" if user.date_joined <= VACATION_RULES.get("new_policy_start_date") else "new_policy"

    @classmethod
    def populate_compliance_history(cls, check_type, keeper_ids=None):
        """
        Populate ComplianceHistory for a given month from the compliance reports.
        check_type: "BASE" or "MONTH"
        keeper_ids: list of user IDs to be marked as compliant regardless of report
        """
        
        keeper_ids = set(keeper_ids or [])
        
        if check_type == "BASE":
            month = Month.objects.current()
            compliance_report = gen_base_compliance_report()
        elif check_type == "MONTH":
            month = Month.get_previous()
            compliance_report = gen_month_compliance_report(month=month)
        else:
            raise ValueError("Invalid check_type. Must be 'BASE' or 'MONTH'.")
        
        if not compliance_report or not compliance_report.get("has_risk"):
            return
        
        users = User.objects.filter(is_active=True, is_invisible=False)
        baseline_objs = [
            cls(
                user=u,
                month=month,
                status=cls.ComplianceStatus.COMPLIANT,
                rule_version=cls._rule_version_for(u),
                reason={},
                source="system"
            )
            for u in users
        ]

        items = compliance_report.get("items", [])
        reasons = {row["user_id"]: row.get("reason") for row in items if "user_id" in row}
        non_compliant_ids = set(reasons.keys()) - keeper_ids

        with transaction.atomic():
            if check_type == "BASE":
                # Bulk create baseline compliant records
                cls.objects.bulk_create(baseline_objs, ignore_conflicts=True)
            
            # Update non-compliant users (excluding keepers)
            for user in users.filter(id__in=non_compliant_ids):
                cls.objects.update_or_create(
                    user=user,
                    month=month,
                    defaults={
                        "status": cls.ComplianceStatus.NONCOMPLIANT,
                        "rule_version": cls._rule_version_for(user),
                        "reason": {"check": check_type, "details": reasons.get(user.id) or {}},
                        "source": "system",
                    },
                )
            
            # Update keepers to compliant
            for user in users.filter(id__in=keeper_ids):
                cls.objects.update_or_create(
                    user=user,
                    month=month,
                    defaults={
                        "status": cls.ComplianceStatus.COMPLIANT,
                        "rule_version": cls._rule_version_for(user),
                        "reason": {"check": check_type, "details": reasons.get(user.id) or {}}, # keep reason for future reference
                        "source": "manual",
                    },
                )
                        
    @classmethod
    def is_eligible(cls):
        """
        Check if the user is eligible based on compliance status.
        """
        # TODO: add method to test for eligibility based on last X months (get x from settings)
        pass
    
    @classmethod
    def mark_compliant_from(cls, user, from_month):
        """
        Mark the user as compliant from the given month onwards until a non-compliant month is found.
        """
        # TODO: add method to get user 'uptodate' with his compliance status
        pass