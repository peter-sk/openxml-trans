from openpyxl import load_workbook

from .base_trans import BaseTranslator

class XLSXTranslator(BaseTranslator):

    def __init__(self, model_name=None, service_url=None, cache_name=None, device=None):
        super(self.__class__, self).__init__(device=device, model_name=model_name, service_url=service_url, cache_name=cache_name)

    def translate_document(self, document):
        for sheet in document.worksheets:
            for row in sheet.rows:
                for cell in row:
                    if cell.data_type == 's':
                        cell.value = self.translate_text(cell.value)

    def load_document(self, document_name):
        return load_workbook(document_name)

    def save_document(self, document, document_name):
        document.save(document_name)
