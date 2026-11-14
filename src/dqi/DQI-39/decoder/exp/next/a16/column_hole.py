"""Exact affine-chart hole encoding from a PROVIDED first transfer column.

All operations are coherent and phase free. The construction cost of the
column is not included here. The field basis is canonical polynomial GF24.
"""
from pathlib import Path
from contextlib import contextmanager
import ast,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'exp/new/a16'),str(ROOT/'exp/new/a10'),
             str(ROOT/'exp/new/a07'),str(ROOT/'playbook/kit'),
             str(ROOT/'playbook/kit/decoder'),str(ROOT/'playbook/kit/decoder/exp/arithmetic')]
import lowclean_norm5log7 as original
from lowclean import mcx_dirty,zero_toggle
ar=original.ar

# Reuse the exact supplied source factorization, extending one further
# quadratic tower. The restricted norm source has absolute trace one or0.
# In a recursively prepared source its final GF8 high block stays raw; the
# absolute trace is that block's bit0, hence handle g[-3].
scope=dict(original.__dict__)
source_path=ROOT/'exp/new/a16/lowclean_norm5log7.py'
text=source_path.read_text();tree=ast.parse(text)
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in
       ('paired_source','source','scale_many','scale')]
for node in nodes:
    source=ast.get_source_segment(text,node)
    if node.name in ('paired_source','source'):source='@contextmanager\n'+source
    if node.name=='paired_source':
        source=source.replace('n in (6,12) and (not trace01 or n==6)',
                              'n in (6,12,24)')
        source=source.replace('b.x(g[0]);yield g[0];b.x(g[0])',
                              'b.x(g[-3]);yield g[-3];b.x(g[-3])')
    exec(compile(source,__file__,'exec'),scope)
paired_source=scope['paired_source']

def equality_toggle(b,r,a,zero_c,F,borrow):
    """F ^= [r=a and c!=0], using arbitrary preserved dirty borrow bits."""
    b.cx(a,r);b.x(r);b.x(zero_c)
    mcx_dirty(b,list(r)+[zero_c],F,borrow)
    b.x(zero_c);b.x(r);b.cx(a,r)

def encode_projective(b,r,F,alpha,zero_c,borrow,reverse=False):
    """Same encoding given alpha=a*inv0(c) and zero_c=[c=0].

    The normalized first-column source is an additional PROVIDED input;
    its construction/erasure is not part of this routine. No clean
    scratch or measurements are needed; at least23 dirty borrow bits
    are preserved. Valid chart images have F=0 whenever zero_c=1.
    """
    if reverse:equality_toggle(b,r,alpha,zero_c,F,borrow)
    b.ccx(F,alpha,r)
    if not reverse:equality_toggle(b,r,alpha,zero_c,F,borrow)

def encode(b,r,F,a,c,borrow,reverse=False):
    """Encode/restore the projective pole using the missing affine image.

    Requires (r,F) from an invertible transfer M applied to[u:1], with
    firstcolumn(a,c). c=0 therefore impliesF=0 anda!=0. The borrow word
    is arbitrary, is preserved, and must contain at least23 distinct bits.
    """
    G=b.alloc_qubits(1)[0]
    with paired_source(b,c)as apply:
        # Every generic source chart chooses a nonzero half whenever its
        # source is nonzero. Thus the final GF8 source is0 iff c was0.
        # It is held in the supplied log encoding, whose zero code is111.
        mcx_dirty(b,list(c[-3:]),G,borrow)
        apply([r])
        if reverse:equality_toggle(b,r,a,G,F,borrow)
        b.ccx(F,a,r)
        if not reverse:equality_toggle(b,r,a,G,F,borrow)
        apply([r],True)
        mcx_dirty(b,list(c[-3:]),G,borrow)
    b.free(G)
