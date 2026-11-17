"""Six-bit signed seed, folded residual parity and ten-row product for INV-74.

Syed Asad Ali is the original builder (NOTICE.txt). The three seed rows use
coefficient cuts 11,10,9. The seed low bit is exactly 1 xor C11 xor C8 on all
4096 root codewords, so HMR erases it with a linear phase correction. The
normalization parity is decoded from flags[2]*flags[3] and folded into the new
low residual coordinate. Ten signed rows then compute a fourteen-bit product.
Carries are rounded at cuts 9..1; the final row has zero incoming carry.

The two finishing outcomes cache a root AND and erase a proved product AND;
they do not encode an instruction stream. Root10/root11 are decoded from the
retained high coefficient chart before coefficient retirement.
"""
from dataclasses import dataclass
import sys
import kickmix as km
from coefficient import retire, disposable


@dataclass
class ProductToken:
    seed_rows: list
    product_rows: list


def forward(cb,ar,v,D,flags,residual_high,*,hold_outcome,top_outcome):
    """Return restored twelve-bit root, product14 and inverse carry debts.

    The caller supplies ten retained root bits, nine high residual bits, the
    coefficient word, and the independent finishing measurement slots.
    """
    v,D,flags=list(v),list(D),list(flags)
    q=km.q
    cache=q(cb.max_qubits-1)
    # A finishing hold cache has fixed external owner q43 and outcome b363.
    held=[]
    while True:
     z=cb.alloc_qubits(1)[0]
     if z==cache:break
     held.append(z)
    for z in reversed(held):cb.free(z)
    for a,b in [(v[2],v[0]),(v[2],v[1]),(v[2],v[3])]:cb.cx(a,b)
    cb.ccx(v[0],v[1],cache);cb.cx(cache,v[3]);cb.cx(v[1],v[0])
    seed=list(cb.alloc_qubits(3));cb.x(km.array(seed));debts=[]
    for i,control in enumerate((v[0],v[1],v[3])):
     cb.x(control);debts.append(ar.forward_signed_row(cb,D,seed,shift=-(11-i),sign=control));cb.x(control)
     z=cb.alloc_qubits(1)[0];cb.x(z);cb.cx(control,z);seed.append(z)
    cb.cx(v[1],v[0]);cb.cx(cache,v[3]);cb.hmr(cache,hold_outcome);cb.ccz(hold_outcome,v[0],v[1])
    for a,b in [(v[2],v[3]),(v[2],v[1]),(v[2],v[0])]:cb.cx(a,b)
    # Release cache back to its original free-pool depth, preserving logical layout.
    free=list(cb.alloc_qubits(44-cb.num_allocated_qubits));cb.free(cache)
    for z in reversed(free):cb.free(z)
    
    low=cb.alloc_qubits(1)[0]
    cb.ccx(flags[2],flags[3],low);cb.cx(low,flags[2]);cb.cx(low,flags[3])
    for i in (0,2,3,4):cb.cx(v[i],low)
    cb.cx(v[0],v[3]);cb.x(v[3]);cb.ccx(seed[5],v[3],low);cb.x(v[3]);cb.cx(v[0],v[3])
    m=retire(cb,seed[0]);cb.push_condition(m);cb.neg();cb.z(D[11]);cb.z(D[8]);cb.pop_condition();cb.free(m)
    word=seed[1:]+[low]+list(residual_high);cb.x(word[14]);C=[False]+D;product=[]
    def product_carry(sign,i):
     shift=9-i;parity=C[9]
     if shift<0:
      cb.cx(parity,sign);cb.x(sign);return sign
     if not shift:return False
     upper,lower=C[shift],C[shift-1];z=cb.alloc_qubits(1)[0]
     if lower is False:
      cb.cx(parity,sign);cb.ccx(upper,sign,z);cb.cx(parity,sign)
     else:
      cb.cx(upper,lower);cb.cx(parity,sign);cb.x(sign);cb.ccx(lower,sign,z);cb.x(sign);cb.cx(parity,sign);cb.cx(upper,lower);cb.cx(upper,z)
     return z
    
    def clear_product(sign,i,z):
     shift=9-i;parity=C[9]
     if shift<0:
      cb.x(sign);cb.cx(parity,sign);return
     if not shift:return
     upper,lower=C[shift],C[shift-1]
     if lower is False:
      cb.cx(parity,sign);cb.del_and(upper,sign,z);cb.cx(parity,sign)
     else:
      cb.cx(upper,z);cb.cx(upper,lower);cb.cx(parity,sign);cb.x(sign);cb.del_and(lower,sign,z);cb.x(sign);cb.cx(parity,sign);cb.cx(upper,lower)
     cb.free(z)
    native_ccx=cb.ccx
    def ccx(a,b,t):
     if getattr(cb,'erase_product_top',False) and t==word[13] and {a,b}=={D[12],word[12]}:
      cb.hmr(t,top_outcome);cb.ccz(top_outcome,a,b)
     else:native_ccx(a,b,t)
    cb.ccx=ccx
    for i in range(10):
     cb.erase_product_top=(i==9)
     sign=word[5+i];target=word[:5+i];source=C[10-i:]
     for z in target:cb.cx(sign,z)
     c=product_carry(sign,i)
     if i<9:debt=disposable(ar,cb,source,target,c,lambda z,i=i,sign=sign:clear_product(sign,i,z))
     else:
      debt=ar.forward_add(cb,source,target,carry_in=c);clear_product(sign,i,c)
     product.append(debt)
     for z in target:cb.cx(sign,z)
    cb.x(word[14])
    
    cb.ccx=native_ccx
    # Decode the two consumed high root owners from a quadratic coefficient chart.
    a=cb.alloc_qubits(1)[0]
    cb.cx(D[10],D[9]);cb.cx(D[11],D[9]);cb.ccx(D[9],D[12],a)
    cb.cx(D[11],D[9]);cb.cx(D[10],D[9])
    v10=cb.alloc_qubits(1)[0]
    for z in D[10:]:cb.cx(z,v10)
    for z in (D[11],v[9],a):cb.cx(z,D[9])
    cb.cx(v[9],D[12]);cb.ccx(D[9],D[12],v10);cb.cx(v[9],D[12])
    for z in reversed((D[11],v[9],a)):cb.cx(z,D[9])
    m=retire(cb,a)
    cb.push_condition(m)
    for z in (D[9],D[10],D[11]):cb.cz(z,D[12])
    cb.pop_condition();cb.free(m)
    v11=cb.alloc_qubits(1)[0]
    for z in D[10:]:cb.cx(z,v11)
    cb.cx(v10,D[10]);cb.cx(v10,D[11]);cb.ccx(D[10],D[11],v11)
    cb.cx(v10,D[11]);cb.cx(v10,D[10])
    cb.x(word[-1]);cb.cx(word[-2],word[-1]);cb.free(word[-1])
    return v+[v10,v11],word[:-1],ProductToken(debts,product)


def build_seed_product_segment():
    """Compile the substage while the surrounding return stages are being lifted."""
    import coefficient as cf
    from arithmetic_prefix import arithmetic_modules
    arithmetic_modules()
    shared=sys.modules['_inv74_shared_arithmetic']
    spec=shared._Spec('_inv74_product_arithmetic',shared._VROOT/'work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/paired_arithmetic.py')
    ar=shared._new_module(spec);sys.modules[spec.name]=ar;spec.loader.exec_module(ar)
    cb=cf._SegmentBuilder()
    D=[km.q(i) for i in (21,34,36,0,30,32,28,35,33,31,20,26,27)]
    D,_=cf.forward(cb,ar,[km.q(i) for i in range(10,16)],D,[km.q(i) for i in range(37,42)],km.q(29))
    before=len(str(cb.finish_circuit()).splitlines())
    forward(cb,ar,[km.q(i) for i in range(10,20)],D,[km.q(i) for i in range(22,26)],
            [km.q(i) for i in range(1,10)],hold_outcome=km.b(363),top_outcome=km.b(364))
    return str(cb.finish_circuit()).splitlines()[before:]
