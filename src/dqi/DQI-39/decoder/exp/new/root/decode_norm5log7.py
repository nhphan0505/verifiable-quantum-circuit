"""Narrow companions with five-T norm scales and seven-T generic log scales."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'exp/new/a16'), str(Path(__file__).resolve().parent)]
import decode_norm5log7_character as prior
from install_ordinary_pair import capture

CAPTURED_OWNERS = len(capture(prior.body))
decode = prior.decode
