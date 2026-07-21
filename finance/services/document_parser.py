import xlrd
from finance.models import UploadedDocument


def process_uploaded_document(document: UploadedDocument) -> None:
    file_path = document.file.path

    workbook = xlrd.open_workbook(document.file.path)
    sheet = workbook.sheet_by_index(0)

    for row_index in range(sheet.nrows):
        row = sheet.row_values(row_index)
        print(row)

    # Example:
    # dataframe = pandas.read_excel(file_path)
    # validate_document(dataframe)
    # save_document_data(document, dataframe)