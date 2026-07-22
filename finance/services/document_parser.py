import openpyxl
from finance.models import UploadedDocument


def process_uploaded_document(document: UploadedDocument) -> None:
    if isinstance(document, str):
        file_path = document
    else:
        file_path = document.file.path
    
    print(file_path)

    workbook = openpyxl.load_workbook(
        file_path,
        read_only=True,
        data_only=True,
    )
    
    sheet = workbook.active
    
    for row in sheet.iter_rows(values_only=True):
        print(list(row))
    
    workbook.close()