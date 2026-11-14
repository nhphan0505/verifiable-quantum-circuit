"""Whole unsynthesis replacement with rank-completed paired routing."""
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path[:0]=[str(H),str(ROOT),str(ROOT/'exp/round7/a03')]
import decode_next_best as prior
from decode_direct_forney import owner_scope
from norm_deferred_flag_return import consume_synthesis,route_words
g=owner_scope(prior.decode)


def decode(b,S,E):
    with b.mark('mask_projection'):mt=g['baseline'].project(b,S,E)
    with b.mark('initial'):g['linear_words'](b,S,g['matrix'])
    with b.mark('extract'):et=g['extraction'](b,S)
    with b.mark('synthesis'):A,B,undo=g['synthesize'](b,S,et['pole'])
    with b.mark('convert'):ct=g['convert_safe'](b,A,B,monic_root=True)
    with b.mark('scan'):g['baseline'].scan(b,A,B,E,skip_points=g['baseline'].SELECTED,node_polynomial=g['Pscan'])
    with b.mark('unconvert'):g['convert_safe'](b,A,B,True,phase_token=ct)
    with b.mark('padded_unsynthesis'):
        heads,real=consume_synthesis(b,A,B,et['pole'],undo)
        route_words(b,[w for h in heads for w in h]+real,S)
    with b.mark('unextract'):g['extraction'](b,S,True,et)
    with b.mark('uninitial'):g['linear_words'](b,S,g['matrix'],True)
    with b.mark('restore_masks'):g['baseline'].restore(b,E,mt)
