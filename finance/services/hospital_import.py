# finance/services/hospital_import.py

from django.db import transaction
from django.db.models import Max

from finance.models import (
    HospitalFinancialBatch,
    HospitalFinancialEntry,
)


@transaction.atomic
def create_original_batch(*, month, document, rows, user):
    latest_version = (
        HospitalFinancialBatch.objects
        .filter(
            month=month,
            batch_type=HospitalFinancialBatch.BatchType.ORIGINAL,
        )
        .aggregate(value=Max("version"))["value"]
        or 0
    )

    batch = HospitalFinancialBatch.objects.create(
        month=month,
        batch_type=HospitalFinancialBatch.BatchType.ORIGINAL,
        version=latest_version + 1,
        uploaded_document=document,
        created_by=user,
    )

    entries = [
        HospitalFinancialEntry(
            batch=batch,
            row_number=index,
            health_plan_name=row["Nome Convênio"],
            procedure_description=row["Descrição Procedimento"],
            provider_name=row["Nome Prestador"],
            doctor=row.get("doctor"),
            transfer_description=row["Descrição Repasse"],
            amount=row["Valor"],
        )
        for index, row in enumerate(rows, start=2)
    ]

    HospitalFinancialEntry.objects.bulk_create(entries)

    return batch