"""Rank-completed raw return with optimal-size linear polynomial quotients.

Each half-pivot adds floor((u+h*x)*S/q) in n field products, where n is
len(S).  This replaces the three-product q-adic residue/carry updates.
It preserves the exact completed permutation and every existing token.
"""
import padded_return as prior
from raw_pair import combine,linear_words,closed_scale24,K
from paired_coefficient import qadic_matrix
from exp.partial_gauge.synthesis_noflag import rank_affine,base


def quotient_add(b,head,source,target,k):
    assert len(target)+1==len(source)
    # Linear frames preserve all source words and do not allocate work.
    linear_words(b,source,qadic_matrix(len(source),k),True)
    linear_words(b,target,qadic_matrix(len(target),k),True)
    for ac,bc,tc in base.quotient_terms(len(source),k):
        rank_affine(b,head,ac,source[1:],bc,target,tc)
    linear_words(b,target,qadic_matrix(len(target),k))
    linear_words(b,source,qadic_matrix(len(source),k))


def bodies(b,A,B,leaders,k=K):
    a1,a2,beta=leaders
    def first():quotient_add(b,A[:2],B+[beta],A[2:]+[a1,a2],k)
    def second():quotient_add(b,B[:2],A[2:]+[a1,a2],B[2:]+[beta],k)
    def second_head(divide):
        source=combine(A[2:4])if len(A)>3 else combine([A[-1],a1])
        closed_scale24(b,combine(B[:2]),source,divide,k)
    return first,second,second_head


sweep=prior.rr.clone(prior.sweep,bodies=bodies)
consume_synthesis=prior.rr.clone(prior.consume_synthesis,sweep=sweep)
route_words=prior.route_words
ROOT=prior.ROOT
