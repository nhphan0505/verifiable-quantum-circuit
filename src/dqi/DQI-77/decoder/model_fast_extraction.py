"""Block-shear implementation/count model for in-place J extraction.

Each shear has sources disjoint from targets; it can use evaluation rank
len(A)+len(B)-1 with two clean field words. The ordinary field model below
checks the block scheduling, using schoolbook arithmetic within shears.
"""
from functools import cache


@cache
def shear_pieces(n, d, constant_b0, m=None):
    """Product pieces grouped by index modulo d; return actual sparse terms."""
    m = (n+1)//2 if m is None else m
    pieces = []
    for residue in range(min(d, m)):
        terms = [(i, j, d*i+j)
                 for i in range(1, (n-1)//d+1)
                 for j in range(residue, m, d)
                 if m <= d*i+j < n and not (constant_b0 and j == 0)]
        if not terms:
            continue
        iset = sorted({i for i,j,k in terms})
        jset = sorted({j for i,j,k in terms})
        targets = sorted({k for i,j,k in terms})
        rank = len(iset)+len(jset)-1
        best_rank,best_kind = min((len(terms),'naive'),(rank,'forward'),
                                  (len(iset)+len(targets)-1,'transpose_right'),
                                  (len(jset)+len(targets)-1,'transpose_left'))
        pieces.append({'terms':terms, 'is':iset, 'js':jset,
                       'rank':best_rank, 'method':best_kind,
                       'evaluation_rank':rank,
                       'transposed_rank':min(len(iset),len(jset))+len(targets)-1})
    return pieces


@cache
def shear_cost(n,d,constant_b0,m):
    return sum(p['rank'] for p in shear_pieces(n,d,constant_b0,m))


@cache
def toeplitz_plan(n,d):
    if n <= d:
        return 0,0
    candidates = [(toeplitz_plan(m,d)[0]+toeplitz_plan(n-m,d)[0]
                   +shear_cost(n,d,False,m),m) for m in range(1,n)]
    return min(candidates)


@cache
def power_plan(n,d):
    if n <= d:
        return 0,0
    candidates = [(power_plan(m,d)[0]+toeplitz_plan(n-m,d)[0]
                   +shear_cost(n,d,True,m),m) for m in range((n+d-1)//d,n)]
    return min(candidates)
