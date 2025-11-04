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
        return "old_policy" if user.date_joined <= VACATION_RULES else "new_policy"

    @classmethod
    def populate_month(cls, check_type, keeper_ids=None):
        """
        Populate ComplianceHistory for a given month from the compliance reports.

        - BASE → month = Month.objects.current()
        - else → month = Month.objects.get_previous()  # month compliance checked when next month unlocks
        """
        keeper_ids = set(keeper_ids or [])

        if check_type == "BASE":
            reports = gen_base_compliance_report()
            month = Month.objects.current()
        else:
            reports = gen_month_compliance_report()
            month = Month.objects.get_previous()

        if not reports or not reports.get("has_risk"):
            return

        items = reports.get("items", [])
        # map user_id → reason payload straight from the report
        raw_at_risk = {row["user_id"]: row.get("reason") for row in items if "user_id" in row}

        # effective at-risk excludes keepers
        effective_at_risk_ids = set(raw_at_risk.keys()) - keeper_ids

        # Fetch all users once (you can narrow this to your roster if you have a scope)
        all_user_ids = set(User.objects.values_list("id", flat=True))
        # If you have a roster queryset, use that instead of all users:
        # roster_user_ids = set(Roster.active_for_month(month).values_list("user_id", flat=True))
        # all_user_ids = roster_user_ids

        rest_ids = all_user_ids - effective_at_risk_ids - keeper_ids

        # Batch fetch users we'll touch
        users_by_id = {u.id: u for u in User.objects.filter(id__in=(effective_at_risk_ids | keeper_ids | rest_ids))}

        with transaction.atomic():
            # 1) Upsert NONCOMPLIANT for effective at-risk (keepers were removed already)
            for uid in effective_at_risk_ids:
                user = users_by_id.get(uid)
                if not user:
                    continue
                cls.objects.update_or_create(
                    user=user,
                    month=month,
                    defaults={
                        "status": cls.ComplianceStatus.NONCOMPLIANT,
                        "rule_version": cls._rule_version_for(user),
                        # JSONField: keep a structured payload
                        "reason": {"check": check_type, "details": raw_at_risk.get(uid) or {}},
                        "source": "system",
                    },
                )

            # 2) Explicitly mark KEEPERS as COMPLIANT (source=manual as you wanted)
            for uid in keeper_ids:
                user = users_by_id.get(uid)
                if not user:
                    continue
                cls.objects.update_or_create(
                    user=user,
                    month=month,
                    defaults={
                        "status": cls.ComplianceStatus.COMPLIANT,
                        "rule_version": cls._rule_version_for(user),
                        "reason": {},  # empty for compliant
                        "source": "manual",
                    },
                )

            # 3) Everyone else → COMPLIANT (source=system)
            for uid in rest_ids:
                user = users_by_id.get(uid)
                if not user:
                    continue
                cls.objects.update_or_create(
                    user=user,
                    month=month,
                    defaults={
                        "status": cls.ComplianceStatus.COMPLIANT,
                        "rule_version": cls._rule_version_for(user),
                        "reason": {},
                        "source": "system",
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