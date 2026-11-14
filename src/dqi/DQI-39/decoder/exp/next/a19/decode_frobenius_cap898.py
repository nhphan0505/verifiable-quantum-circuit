"""Whole width candidate with the exact711T borrowed source circuit."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'exp/next/a13')]
p=ROOT/'exp/next/a13/decode_inv72_cap898.py'
text=p.read_text().replace('import no_clean_source12_inv72 as borrowed_source',
                          'import no_clean_source12_frobenius as borrowed_source')
scope={'__name__':'a19_frobenius_installer','__file__':str(p)}
exec(compile(text,str(p),'exec'),scope)
decode=scope['decode']
INSTALLATION_COUNT=len(scope['INSTALLED'])
