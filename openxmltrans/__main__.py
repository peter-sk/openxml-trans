from sys import argv

from . import EXT_TO_TRANS

in_file_name = argv[1]
out_file_name = argv[2]
ext = in_file_name.split(".")[-1].lower()
trans_class = EXT_TO_TRANS[ext]
if trans_class:
    trans = trans_class()
    trans.translate(in_file_name, out_file_name)
else:
    raise RuntimeError(f"Unknown extension {ext} - please select one of {EXT_TO_TRANS.keys()}!")