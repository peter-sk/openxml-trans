from .docx_trans import DOCXTranslator
from .pptx_trans import PPTXTranslator
from .xlsx_trans import XLSXTranslator

EXT_TO_TRANS = {
    "docx": DOCXTranslator,
    "pptx": PPTXTranslator,
    "xlsx": XLSXTranslator,
}
