import openpyxl
from django.db import transaction
from django.db.models import Max
from core.models import User
from finance.models import (
    UploadedDocument,
    HospitalFinancialBatch,
    HospitalFinancialEntry,
    )


from django.db import transaction
from django.db.models import Max


@transaction.atomic
def create_original_batch(month, user):
    latest_version = (
        HospitalFinancialBatch.objects
        .select_for_update()
        .filter(
            month=month,
            batch_type=HospitalFinancialBatch.BatchType.ORIGINAL,
        )
        .aggregate(max_version=Max("version"))
        ["max_version"]
        or 0
    )

    return HospitalFinancialBatch.objects.create(
        month=month,
        batch_type=HospitalFinancialBatch.BatchType.ORIGINAL,
        version=latest_version + 1,
        source_batch=None,
        created_by=user,
    )

def process_uploaded_document(document: UploadedDocument) -> None:
    # change after testing to use document.file.path directly
    if isinstance(document, str):
        file_path = document
    else:
        file_path = document.file.path

    workbook = openpyxl.load_workbook(
        file_path,
        read_only=True,
        data_only=True,
    )
    
    sheet = workbook.active
    for row in sheet.iter_rows(values_only=True):
        code = row[0]
        health_plan_name = row[2]
        procedure_description = row[3]
        provider_name = row[4]
        transfer_description = row[5]
        payment = row[7]

        if not code:
            continue

        if not isinstance(code, int) and not code.isdigit():
            continue

        if not procedure_description:
            continue

        
    #     if payment_description not in per_item:
    #         per_item[payment_description] = {}

    #     doctor_name = " ".join([name.casefold().strip() for name in doctor_name.split()])
    #     if doctor_name not in per_item[payment_description]:
    #         doctor = User.objects.filter(search_name=doctor_name).first()
    #         if not doctor:
    #             print(f"Doctor not found for name: {doctor_name}")
    #             continue
    #         per_item[payment_description][doctor.crm] = 0

    #     per_item[payment_description][doctor.crm] += int(payment)

    # for payment_description, doctors in per_item.items():
    #     for crm, total_payment in doctors.items():
    #         print(f"Payment Description: {payment_description}, Doctor CRM: {crm}, Total Payment: {total_payment}")

    workbook.close()