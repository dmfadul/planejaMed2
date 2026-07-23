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
    doc_test = set()
    for row in sheet.iter_rows(values_only=True):
        code, _, _, procedure, doctor_name, payment_description, _, payment = list(row)
        if not code:
            continue

        if not isinstance(code, int) and not code.isdigit():
            continue
        
        if not procedure:
            continue
        
        if procedure not in per_item:
            per_item[procedure] = {}

        doctor_name = " ".join([name.title().strip() for name in doctor_name.split()])
        if doctor_name not in doc_test:
            doctor = User.objects.filter(name__iexact=doctor_name).first()
            doc_test.add((doctor_name, doctor))

    
        # print(code, procedure, doctor_name, payment_description, payment)
    for item in doc_test:
        print(item)

    workbook.close()