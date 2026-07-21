import pandas as pd
from finance.models import UploadedDocument


def process_uploaded_document(document: UploadedDocument) -> None:
    file_path = document.file.path
    dataframe = pandas.read_excel(file_path)

    # Example:
    # validate_document(dataframe)
    # save_document_data(document, dataframe)