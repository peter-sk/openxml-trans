from .docx_trans import DOCXTranslator
from .pptx_trans import PPTXTranslator

EXT_TO_TRANS = {
    "docx": DOCXTranslator,
    "pptx": PPTXTranslator,
}
