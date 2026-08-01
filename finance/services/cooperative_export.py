# finance/services/cooperative_export.py
# will adapt after getting the rest of the code to work

from django.db import transaction
from django.db.models import Max

from finance.models import (
    HospitalFinancialBatch,
    HospitalFinancialEntry,
)


@transaction.atomic
def create_coop_batch(*, original_batch, allocated_amounts, user):
    latest_version = (
        HospitalFinancialBatch.objects
        .filter(
            source_batch=original_batch,
            batch_type=HospitalFinancialBatch.BatchType.COOP,
        )
        .aggregate(value=Max("version"))["value"]
        or 0
    )

    batch = HospitalFinancialBatch.objects.create(
        month=original_batch.month,
        batch_type=HospitalFinancialBatch.BatchType.COOP,
        version=latest_version + 1,
        source_batch=original_batch,
        created_by=user,
    )

    entries = [
        HospitalFinancialEntry(
            batch=batch,
            source_entry=entry,
            row_number=entry.row_number,
            health_plan_name=entry.health_plan_name,
            procedure_description=entry.procedure_description,
            provider_name=entry.provider_name,
            transfer_description=entry.transfer_description,
            amount=allocated_amounts[entry.id],
        )
        for entry in original_batch.entries.all()
    ]

    HospitalFinancialEntry.objects.bulk_create(entries)

    return batch