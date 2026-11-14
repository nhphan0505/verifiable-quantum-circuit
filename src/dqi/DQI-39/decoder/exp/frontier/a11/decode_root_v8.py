"""A11 CRT reverse on root v8, preserving all previous exact front kernels."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'root')]
import decode_combo_v8
from decode_low_crt import install
decode=install(decode_combo_v8.decode)
