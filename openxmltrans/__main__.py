from click import argument, command, option, Path
from sys import argv

from . import EXT_TO_TRANS

@command()
@argument(
    "in-file-name",
    type=Path(exists=True),
)
@argument(
    "out-file-name",
    type=Path(exists=False),
)
@option(
    "--model-name",
    "-m",
    default="Helsinki-NLP/opus-mt-%s-%s",
    show_default=True,
    help="""Path or Huggingface Hub name template of the model to load.""",
)
@option(
    "--service-url",
    "-u",
    default=None,
    show_default=True,
    help="""URL for translation web service.""",
)
@option(
    "--cache-name",
    "-c",
    default=None,
    help="""Name of the cache file. Empty string indicates memory-only cache. Default is no cache."""
)
@option(
    "--device",
    "-d",
    default=None,
    help="""CPU or GPU to user. Default is auto detection."""
)
@option(
    "--clean-text",
    "-t",
    default=False,
    help="""Whether to clean the text."""
)
@option(
    "--original-language",
    "-o",
    default="da",
    help="""Language of the original document."""
)
@option(
    "--result-language",
    "-r",
    default="en",
    help="""Language of the result document."""
)
def main(in_file_name, out_file_name, model_name, service_url, cache_name, device, clean_text, original_language, result_language):
    ext = in_file_name.split(".")[-1].lower()
    if ext == "pdf":
        from pdf2docx import parse
        parse(in_file_name, in_file_name+".docx")
        in_file_name += ".docx"
        ext = "docx"
    trans_class = EXT_TO_TRANS.get(ext, None)
    if trans_class is not None:
        trans = trans_class(model_name=model_name, service_url=service_url, cache_name=cache_name, device=device, clean_text=clean_text, original_language=original_language, result_language=result_language)
        trans.translate(in_file_name, out_file_name)
    else:
        raise RuntimeError(f"Unknown extension {ext} - please select one of {', '.join(EXT_TO_TRANS.keys())}!")

main()