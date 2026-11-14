"""Carry-over converter plus combo exact substitutions, cycle-safe scope clone."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ported as p
from rebind_graph import private_rebind
convert_safe = private_rebind(p.convert_safe, p.base.replacements, p.ROOT)
decode = p.clone(p.decode, dict(p.decode.__globals__, convert_safe=convert_safe))
