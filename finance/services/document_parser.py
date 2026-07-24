import openpyxl
from core.models import User
from finance.models import UploadedDocument


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
    per_item = {}
    for row in sheet.iter_rows(values_only=True):
        code, _, _, procedure, doctor_name, payment_description, _, payment = list(row)

        if not code:
            continue

        if not isinstance(code, int) and not code.isdigit():
            continue
        
        if not procedure:
            continue
        
        if payment_description not in per_item:
            per_item[payment_description] = {}

        doctor_name = " ".join([name.casefold().strip() for name in doctor_name.split()])
        if doctor_name not in per_item[payment_description]:
            doctor = User.objects.filter(search_name=doctor_name).first()
            if not doctor:
                print(f"Doctor not found for name: {doctor_name}")
                continue
            per_item[payment_description][doctor.crm] = 0

        per_item[payment_description][doctor.crm] += int(payment)

    for payment_description, doctors in per_item.items():
        for crm, total_payment in doctors.items():
            print(f"Payment Description: {payment_description}, Doctor CRM: {crm}, Total Payment: {total_payment}")

    workbook.close()