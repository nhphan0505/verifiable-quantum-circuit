"""Entry point for the complete front-half research decoder."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent/'exp/frontier/root'))
from decode_combo_v18 import decode
