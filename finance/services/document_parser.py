import openpyxl
from core.models import User
from finance.models import UploadedDocument
from decimal import Decimal, InvalidOperation


def parse_decimal(value):
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    text = (
        text
        .replace("R$", "")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )

    try:
        return Decimal(text)
    except InvalidOperation:
        return None


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
    
    rows = []
    sheet = workbook.active
    for row in sheet.iter_rows(values_only=True):
        health_plan_name = row[2]
        procedure_description = row[3]
        provider_name = row[4]
        transfer_description = row[5]
        payment = parse_decimal(row[7])

        if not (provider_name and payment):
            continue

        doctor_name = " ".join([name.casefold().strip() for name in provider_name.split()])
        doctor = User.objects.filter(search_name=doctor_name).first()
        
        rows.append({
            "Nome Convênio": health_plan_name or "",
            "Descrição Procedimento": procedure_description or "",
            "Nome Prestador": provider_name,
            "doctor": doctor,
            "Descrição Repasse": transfer_description or "",
            "Valor": payment,
        })

    workbook.close()
    return rows