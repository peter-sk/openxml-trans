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
    default=None,
    show_default=True,
    help="""Path or Huggingface Hub name of the model to load.""",
)
@option(
    "--service-url",
    "-s",
    default=None,
    show_default=True,
    help="""URL for translation web service.""",
)
@option(
    "--device",
    "-d",
    default=None,
    help="""CPU or GPU to user. Default is auto detection."""
)
def main(in_file_name, out_file_name, model_name, service_url, device):
    ext = in_file_name.split(".")[-1].lower()
    trans_class = EXT_TO_TRANS.get(ext, None)
    if trans_class is not None:
        trans = trans_class(model_name=model_name, service_url=service_url, device=device)
        trans.translate(in_file_name, out_file_name)
    else:
        raise RuntimeError(f"Unknown extension {ext} - please select one of {', '.join(EXT_TO_TRANS.keys())}!")

main()