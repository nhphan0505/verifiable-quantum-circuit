"""Exact width-neutral synthesis kernels."""
from exp.fold_joint import kernel as fold
import truncated_small as small

def low_product(b, head, A, B):
    k = len(B)
    if k in (2, 3):
        small.accumulate(b, list(head[0])+list(head[1]),
                         [q for w in A[:k] for q in w],
                         [q for w in B for q in w], k)
    else:
        fold.low_product(b, head, A, B)
