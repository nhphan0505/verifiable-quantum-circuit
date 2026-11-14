"""Conservative six-fresh scalar hook on the parent's v11 decoder."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'root')]
import decode_combo_v11
from decode_inverse20_12 import install
decode=install(decode_combo_v11.decode)
