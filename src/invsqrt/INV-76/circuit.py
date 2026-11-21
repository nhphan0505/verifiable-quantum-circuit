"""
Interpolation and reversible phase cleanup.

The 22-qubit input is normalized by the shared leading-bit chain and staged shifts. The parity and seven address bits select one of 256 coefficient rows. The builder splits the quadratic contribution into coarse and residual pieces, interpolates with the fixed-width updates in InvSqrtCfg, and reuses the lookup and arithmetic workspace. _adaptive_lookup changes lookup realization according to the table pattern. _folded_gadd and _shift_pruned keep the low and high arithmetic paths reversible.

The fixed integer table and rational phase angles preserve the upstream approximation. Scratch is cleared by inverse arithmetic or HMR. _demolish returns measurement outcomes to _repair_anf for address-dependent phase correction. The last joint top-normalization repair handles the parity and pending-measurement cases before the flags are freed. Correctness requires input restoration and phase within the official verifier tolerance across the 3,133,452-input domain.

Run solution.py with configs/notebook-native.json in the repository Python
3.13 environment. The output is checked separately by the official verifier.
See NOTICE.md for upstream attribution.
"""

from fractions import Fraction
from dataclasses import dataclass

import kickmix as km
import numpy as np

# Coefficient table: (exponent-parity, 7-bit address) -> (K2, K1, K0), plus base/step interpolation rows.
INVSQRT_R3_DATA = {
    "params": [9, 19, 26, 2, [5]],
    "interpolation": {
        "fraction_bits": 3, "remainder_bits": 3, "step_width": 4, "update_width": 8,
        "rows": (
            [[126,9]]*8 + [[108,7]]*8 + [[94,6]]*8 + [[83,5]]*8 +
            [[73,4]]*8 + [[65,3]]*8 + [[58,2]]*4 + [[57,2]]*4 +
            [[52,2]]*4 + [[51,0]]*2 + [[50,0],[49,0]] +
            [[47,2]]*4 + [[46,2]]*4 + [[42,1]]*8 +
            [[39,0]]*4 + [[39,2]]*4 + [[35,2]]*8 + [[32,1]]*8 +
            [[30,0]]*4 + [[29,0]]*4 + [[27,0]]*4 + [[26,0]]*4 +
            [[25,0]]*5 + [[24,0]]*3 +
            [[178,13]]*8 + [[154,11]]*8 + [[134,7]]*8 + [[117,7]]*8 +
            [[103,6]]*8 + [[92,5]]*8 + [[82,4]]*8 + [[73,4]]*8 +
            [[66,3]]*8 + [[60,3]]*8 + [[54,2]]*8 + [[50,2]]*8 +
            [[45,2]]*8 + [[41,2]]*8 + [[38,1]]*8 + [[35,1]]*8
        )
    },
    "rows": [
        [134,184284,189442912],[132,182154,188710052],[130,180064,187985631],[128,178014,187269491],
        [124,176003,186561483],[122,174029,185861435],[120,172091,185169211],[118,170190,184484662],
        [115,168323,183807656],[113,166490,183138044],[111,164690,182475698],[109,162922,181820487],
        [107,161186,181172283],[105,159481,180530965],[103,157805,179896407],[101,156158,179268497],
        [100,154540,178647110],[98,152949,178032146],[96,151386,177423488],[94,149849,176821030],
        [94,148338,176224660],[92,146852,175634293],[90,145391,175049821],[88,143953,174471143],
        [88,142540,173898159],[86,141149,173330793],[86,139781,172768935],[84,138436,172212514],
        [82,137110,171661436],[80,135807,171115614],[80,134523,170574958],[78,133260,170039402],
        [77,132017,169508856],[75,130792,168983250],[75,129587,168462493],[73,128400,167946531],
        [73,127231,167435271],[71,126080,166928663],[71,124945,166426615],[69,123828,165929081],
        [68,122727,165435977],[68,121643,164947238],[66,120574,164462814],[66,119521,163982626],
        [64,118483,163506628],[64,117461,163034742],[62,116452,162566926],[62,115458,162103108],
        [60,114478,161643246],[60,113512,161187265],[58,112560,160735131],[58,111621,160286773],
        [57,110695,159842149],[57,109781,159401199],[55,108880,158963889],[55,107991,158530151],
        [54,107114,158099947],[54,106249,157673222],[52,105396,157249944],[52,104553,156830046],
        [51,103722,156413500],[51,102903,156000250],[50,102094,155590264],[49,101295,155183492],
        [49,100507,154779890],[49,99728,154379422],[47,98960,153982054],[47,98201,153587730],
        [46,97453,153196425],[46,96714,152808091],[44,95984,152422703],[44,95263,152040211],
        [43,94552,151660585],[43,93848,151283785],[43,93154,150909781],[43,92469,150538535],
        [41,91791,150170027],[41,91122,149804203],[41,90461,149441037],[41,89807,149080500],
        [39,89162,148722570],[39,88525,148367196],[39,87895,148014360],[39,87272,147664028],
        [39,86657,147316170],[39,86048,146970762],[37,85448,146627778],[37,84853,146287178],
        [37,84267,145948938],[37,83686,145613036],[35,83112,145279450],[35,82544,144948138],
        [35,81983,144619082],[35,81429,144292257],[33,80881,143967645],[33,80339,143645207],
        [33,79802,143324927],[33,79272,143006779],[33,78748,142690739],[33,78229,142376787],
        [31,77716,142064905],[31,77208,141755057],[31,76706,141447225],[31,76210,141141391],
        [30,75719,140837539],[30,75233,140535635],[30,74752,140235663],[30,74277,139937605],
        [29,73806,139641443],[29,73341,139347148],[29,72879,139054708],[29,72424,138764100],
        [27,71973,138475316],[27,71526,138188320],[27,71084,137903100],[27,70647,137619640],
        [26,70214,137337922],[26,69785,137057926],[26,69361,136779636],[26,68941,136503032],
        [25,68526,136228104],[25,68114,135954826],[25,67706,135683186],[25,67303,135413170],
        [25,66903,135144756],[24,66508,134877940],[24,66116,134612692],[24,65728,134349002],
        [190,260618,267912733],[186,257604,266876317],[184,254649,265851829],[180,251750,264839058],
        [176,248905,263837776],[172,246114,262847766],[170,243374,261868805],[166,240685,260900717],
        [164,238044,259943273],[162,235452,258996294],[158,232907,258059602],[156,230407,257132988],
        [152,227952,256216297],[150,225540,255309331],[146,223170,254411939],[144,220841,253523934],
        [141,218553,252645166],[139,216303,251775472],[137,214092,250914696],[135,211918,250062687],
        [133,209781,249219303],[131,207680,248384395],[129,205614,247557821],[127,203582,246739444],
        [124,201582,245929136],[122,199616,245126758],[120,197681,244332178],[118,195777,243545277],
        [116,193903,242765929],[114,192059,241994019],[112,190245,241229423],[110,188458,240472031],
        [109,186700,239721722],[107,184968,238978398],[105,183264,238241948],[103,181585,237512262],
        [103,179932,236789233],[101,178303,236072775],[99,176699,235362783],[97,175119,234659159],
        [97,173563,233961797],[95,172029,233270625],[95,170518,232585534],[93,169029,231906454],
        [91,167561,231233288],[89,166115,230565950],[89,164688,229904346],[87,163283,229248415],
        [86,161897,228598063],[84,160531,227953219],[84,159184,227313793],[82,157855,226679727],
        [82,156545,226050927],[80,155254,225427342],[80,153979,224808878],[78,152723,224195488],
        [77,151482,223587086],[75,150259,222983616],[75,149052,222384996],[73,147861,221791180],
        [73,146686,221202087],[71,145527,220617673],[71,144382,220037857],[69,143253,219462601],
        [69,142138,218891821],[69,141038,218325473],[67,139951,217763505],[67,138879,217205848],
        [65,137820,216652462],[65,136774,216103274],[63,135742,215558250],[63,134723,215017324],
        [63,133716,214480446],[63,132722,213947572],[61,131740,213418658],[61,130771,212893639],
        [59,129812,212372483],[59,128865,211855127],[57,127931,211341545],[57,127007,210831671],
        [56,126095,210325473],[56,125193,209822899],[54,124302,209323919],[54,123422,208828475],
        [54,122551,208336532],[54,121691,207848048],[52,120841,207362994],[52,120001,206881312],
        [52,119170,206402970],[52,118350,205927932],[50,117538,205456166],[50,116736,204987620],
        [50,115943,204522264],[50,115158,204060064],[48,114383,203600993],[48,113616,203144995],
        [47,112858,202692053],[47,112108,202242123],[45,111366,201795185],[45,110633,201351191],
        [45,109907,200910111],[45,109190,200471917],[43,108480,200036589],[43,107778,199604073],
        [43,107083,199174353],[43,106396,198747396],[41,105716,198323182],[41,105043,197901664],
        [41,104378,197482822],[41,103719,197066628],[39,103068,196653062],[39,102422,196242082],
        [39,101785,195833668],[39,101153,195427794],[39,100528,195024432],[39,99909,194623556],
        [37,99298,194225152],[37,98692,193829176],[37,98091,193435613],[37,97497,193044437],
        [36,96909,192655629],[36,96327,192269157],[36,95751,191884999],[36,95180,191503137],
        [34,94616,191123553],[34,94057,190746211],[34,93502,190371093],[34,92954,189998181]
    ]
}
assert len(INVSQRT_R3_DATA['rows']) == 256 and len(INVSQRT_R3_DATA['interpolation']['rows']) == 256, 'coefficient table is incomplete'

class InvSqrtCfg:
    DB = 14
    NSTAGES = [(4, 16), (3, 8), (2, 4), (1, 2), (0, 1)]
    def __init__(self, f2, f1, fyr, gy, drop2=()):
        self.f2, self.f1, self.fyr, self.gy = f2, f1, fyr, gy
        self.fy = fyr + gy
        self.w2 = f2 - 1
        self.sh2 = [f2 + 22 - i - f1 for i in range(14)]
        self.sh1 = [f1 + 22 - i - self.fy for i in range(14)]
        self.drop2 = set(drop2)
    def rrow_list(self):
        return [i for i in reversed(range(14)) if i not in self.drop2 and self.sh2[i] < self.w2]

def _rd(v, s):
    if s < 0: return v << (-s)
    r = v >> s
    if s >= 1: r = r + ((v >> (s - 1)) & 1)
    return r

def _pipeline(cfg, K2, K1, d):
    sig = [2 * ((d >> i) & 1) - 1 for i in range(14)]
    R = np.full_like(d, K1)
    for i in cfg.rrow_list(): R = R - sig[i] * _rd(K2, cfg.sh2[i])
    Q = np.zeros_like(d)
    for i in reversed(range(14)): Q = Q + sig[i] * _rd(R, cfg.sh1[i])
    return R, Q

def _layout_and_prepare(cfg, tabs):
    LB, S = cfg.fy - 7, cfg.fy - 8
    d = np.arange(1 << 14, dtype=np.int64)
    Rmax = 0; per = {}; minimum = {}; maxima = {}
    for key, (K2, K1, K0) in tabs.items():
        R, Q = _pipeline(cfg, K2, K1, d)
        minimum[key] = int(R.min()); maxima[key] = int(R.max())
        Rmax = max(Rmax, int(R.max()), K1)
        per[key] = (int(Q.min()), int(Q.max()))
    lo_tab, hi_tab = {}, {}
    for key, (K2, K1, K0) in tabs.items():
        qmin, qmax = per[key]
        base = K0 % (1 << S); j = 0
        while base + j * (1 << S) - qmax < 0: j += 1
        k0lo = base + j * (1 << S)
        lo_tab[key] = k0lo; hi_tab[key] = (K0 - k0lo) >> S
    whi = max(max(hi_tab.values()).bit_length(), 1)
    for block in range(1, Rmax.bit_length()):
        bases = {k: v >> block for k, v in minimum.items()}
        if all(0 <= tabs[k][1] - (v << block) < (1 << (block + 1)) and maxima[k] - (v << block) < (1 << (block + 1)) for k, v in bases.items()):
            break
    lay = dict(w1=Rmax.bit_length(), LB=LB, S=S, whi=whi, lo=lo_tab, hi=hi_tab)
    sp = dict(block=block, rw=block+1, cw=Rmax.bit_length()-block, coarse=bases,
              residual={k: tabs[k][1] - (v << block) for k, v in bases.items()})
    return lay, sp

def _phase_all(b, controls):
    k = len(controls)
    if k == 1: b.z(controls[0]); return
    if k == 2: b.cz(controls[0], controls[1]); return
    anc = b.alloc_qubits(k - 2)
    b.init_and(controls[0], controls[1], anc[0])
    for j in range(1, k - 2): b.init_and(anc[j - 1], controls[j + 1], anc[j])
    b.cz(anc[k - 3], controls[k - 1])
    for j in reversed(range(1, k - 2)): b.del_and(anc[j - 1], controls[j + 1], anc[j])
    b.del_and(controls[0], controls[1], anc[0])
    b.free(anc)

def _folded_gadd(b, a, t, cin=None, sub=False):
    """Controlled-free ripple add (or subtract) of `a` into `t` with optional carry-in; carries are measurement-uncomputed."""
    a, t = list(a), list(t); o, n = len(a), len(t)
    if sub:
        for q in t: b.x(q)
    if n == 1:
        if o: b.cx(a[0], t[0])
        if cin is not None: b.cx(cin, t[0])
        if sub:
            for q in t: b.x(q)
        return
    count = max(0, n - 2)
    c = list(b.alloc_qubits(count)) if count else []
    def C(i): return cin if i == 0 else c[i - 1]
    for i in range(n - 2):
        if i == 0 and cin is None:
            if o: b.init_and(a[0], t[0], C(1))
        elif i < o:
            b.cx(C(i), a[i]); b.cx(C(i), t[i])
            b.init_and(a[i], t[i], C(i + 1)); b.cx(C(i), C(i + 1))
        else:
            b.init_and(C(i), t[i], C(i + 1))
    i = n - 2; carry = C(i)
    if carry is None:
        if i < o: b.ccx(a[i], t[i], t[-1]); b.cx(a[i], t[i])
    elif i < o:
        b.cx(carry, a[i]); b.cx(carry, t[i])
        b.ccx(a[i], t[i], t[-1]); b.cx(carry, t[-1])
        b.cx(carry, a[i]); b.cx(a[i], t[i])
    else:
        b.ccx(carry, t[i], t[-1]); b.cx(carry, t[i])
    if n - 1 < o: b.cx(a[n - 1], t[n - 1])
    for i in reversed(range(n - 2)):
        if i == 0 and cin is None:
            if o: b.del_and(a[0], t[0], C(1)); b.cx(a[0], t[0])
        elif i < o:
            b.cx(C(i), C(i + 1)); b.del_and(a[i], t[i], C(i + 1))
            b.cx(C(i), a[i]); b.cx(a[i], t[i])
        else:
            b.del_and(C(i), t[i], C(i + 1)); b.cx(C(i), t[i])
    if count: b.free(c)
    if sub:
        for q in t: b.x(q)

def _shift_pruned(b, flags, word, L, inverse):
    stages = [(1, 1), (2, 2), (3, 4), (4, 8)]; occ = []; n = L
    for k, d in stages:
        occ.append(min(n, L + 2) if k == 4 else n); n = min(n + d, len(word))
    seq = list(enumerate(stages))
    if inverse: seq = seq[::-1]
    for j, (k, d) in seq:
        indices = range(occ[j]) if inverse else reversed(range(occ[j]))
        for i in indices:
            if i + d < len(word):
                if i + d >= L + sum(amt for _, amt in stages[:j]):
                    if inverse: b.cx(word[i + d], word[i]); b.del_and(flags[k], word[i], word[i + d])
                    else: b.init_and(flags[k], word[i], word[i + d]); b.cx(word[i + d], word[i])
                else:
                    b.cswap(flags[k], word[i], word[i + d])

def _demolish(b, register):
    """Measure-and-release a register (HMR); returns the classical bits that parametrize the phase repair."""
    bits = b.alloc_bits(len(register))
    for q, m in zip(register, bits): b.hmr(q, m)
    return list(bits)

def _repair_anf(b, address, table, measurements, low_bits=4):
    """Apply, in one shared pass, the Z-type phase corrections caused by every earlier demolish step."""
    address = list(address); bits = list(measurements); coef = list(table)
    for i in range(len(address)):
        for mask in range(len(coef)):
            if mask & (1 << i): coef[mask] ^= coef[mask ^ (1 << i)]
    def monomials(reg):
        nodes = {1 << i: q for i, q in enumerate(reg)}; undo = []
        for mask in range(1, 1 << len(reg)):
            if mask in nodes: continue
            bit = mask & -mask; left = nodes[mask ^ bit]; right = nodes[bit]
            target = b.alloc_qubits(1)[0]; b.init_and(left, right, target)
            nodes[mask] = target; undo.append((left, right, target))
        return nodes, undo
    lo, lundo = monomials(address[:low_bits]); hi, hundo = monomials(address[low_bits:])
    one = b.alloc_qubits(1)[0]; b.x(one)
    for mask, word in enumerate(coef):
        l = mask & ((1 << low_bits) - 1); h = mask >> low_bits
        while word:
            pos = (word & -word).bit_length() - 1; b.push_condition(bits[pos])
            if l and h: b.cz(lo[l], hi[h])
            else: b.z(lo[l] if l else hi[h] if h else one)
            b.pop_condition(); word &= word - 1
    b.x(one); b.free(one)
    for left, right, target in reversed(hundo + lundo):
        b.del_and(left, right, target); b.free(target)
    for bit in bits: b.free(bit)

def _anf_lookup(b, address, target, table):
    address = list(address); coef = list(table); n = len(address)
    for i in range(n):
        for mask in range(1 << n):
            if (mask >> i) & 1: coef[mask] ^= coef[mask ^ (1 << i)]
    active = {}
    def needed(mask, nextbit):
        active[mask] = bool(coef[mask])
        for j in range(nextbit, n): active[mask] |= needed(mask | (1 << j), j + 1)
        return active[mask]
    for i in range(n): needed(1 << i, i + 1)
    def xor(val, ctrl=None):
        for i, q in enumerate(target):
            if (val >> i) & 1:
                if ctrl is None: b.x(q)
                else: b.cx(ctrl, q)
    xor(coef[0])
    def visit(mask, ctrl, nextbit):
        xor(coef[mask], ctrl)
        for j in range(nextbit, n):
            child = mask | (1 << j)
            if not active[child]: continue
            q = b.alloc_qubits(1)[0]; b.init_and(ctrl, address[j], q)
            visit(child, q, j + 1); b.del_and(ctrl, address[j], q); b.free(q)
    for i in range(n):
        if active[1 << i]: visit(1 << i, address[i], i + 1)

def _adaptive_lookup(b, address, target, table):
    """Unary-iteration lookup that stops descending as soon as a sub-table is constant."""
    address = list(address)
    def xor_word(val, ctrl):
        for i, q in enumerate(target):
            if (val >> i) & 1:
                if ctrl is None: b.x(q)
                else: b.cx(ctrl, q)
    def walk(bits, rows, parent):
        if len(set(rows)) == 1: xor_word(rows[0], parent); return
        bit = bits[-1]; half = len(rows) // 2
        if parent is None:
            b.x(bit); walk(bits[:-1], rows[:half], bit); b.x(bit)
            walk(bits[:-1], rows[half:], bit)
        else:
            tmp = b.alloc_qubits(1)[0]
            b.x(bit); b.init_and(parent, bit, tmp); b.x(bit)
            walk(bits[:-1], rows[:half], tmp)
            b.cx(parent, tmp); walk(bits[:-1], rows[half:], tmp); b.cx(parent, tmp)
            b.x(bit); b.del_and(parent, bit, tmp); b.x(bit); b.free(tmp)
    walk(address, list(table), None)

def build_circuit():
    c = InvSqrtCfg(*INVSQRT_R3_DATA['params'])
    tabs = {(e, a): tuple(INVSQRT_R3_DATA['rows'][128 * e + a]) for e in range(2) for a in range(128)}
    interp = INVSQRT_R3_DATA['interpolation']
    lay, sp = _layout_and_prepare(c, tabs)

    b = km.CircuitBuilder()
    x = b.create_quantum_register(22, name='x')
    flags = b.alloc_qubits(4)
    f = [x[21]] + list(flags)

    # Shared-prefix normalisation with the parity folded into the flags
    bits = [x[21 - m] for m in range(20)]
    b.x(km.array(bits))
    chain = b.alloc_qubits(19)
    b.init_and(bits[0], bits[1], chain[0])
    for m in range(1, 19): b.init_and(chain[m - 1], bits[m + 1], chain[m])
    p = {j: chain[4 * j - 2] for j in range(1, 6)}
    b.cx(p[4], f[4])
    b.cx(p[2], f[3]); b.cx(p[4], f[3])
    for j in range(1, 6): b.cx(p[j], f[2])
    for m in reversed(range(1, 19)): b.del_and(chain[m - 1], bits[m + 1], chain[m])
    b.del_and(bits[0], bits[1], chain[0])
    b.free(chain)
    b.x(km.array(bits))

    for k, amount in c.NSTAGES[:-1]:
        if amount == 2:
            top = x[20:22]; b.x(top); b.ccx(top[0], top[1], f[1]); b.x(top)
        for i in reversed(range(22 - amount)):
            b.cswap(f[k], x[i], x[i + amount])
    b.x(x[21]); b.left_rotate(x[:21], 1, control=x[21]); b.cx(x[21], x[0])

    res, coarse, low, high = [b.alloc_qubits(n) for n in [sp['rw'], sp['cw'], lay['LB'], lay['whi']]]
    full = km.array(list(low) + list(res) + list(high) + list(coarse))
    rest = km.array(list(low) + list(res) + list(coarse))
    ft, rt, ht = [], [], []
    for e in range(2):
        for a in range(128):
            k = (e, a)
            common = lay['lo'][k] | (sp['residual'][k] << lay['LB'])
            rt.append(common | (sp['coarse'][k] << (lay['LB'] + sp['rw'])))
            ft.append(common | (lay['hi'][k] << (lay['LB'] + sp['rw'])) | (sp['coarse'][k] << (lay['LB'] + sp['rw'] + lay['whi'])))
            ht.append(lay['hi'][k])

    address = km.array(list(x[14:21]) + [f[0]])
    delta = x[:14]
    c2 = None
    step_masks = []

    def phase(reg, lowbit):
        ext = b.alloc_qubits(10)
        word = km.array(list(reg) + list(ext))
        _shift_pruned(b, f, word, len(reg), False)
        for i, q in enumerate(word):
            ex = lowbit + i - c.fy - 10
            if ex < 0: b.z_pow(q, Fraction(2)**(ex + 1))
        _shift_pruned(b, f, word, len(reg), True)
        b.free(ext)

    def load_curvature():
        nonlocal c2
        c2 = b.alloc_qubits(c.w2)
        sw = interp['step_width']; step = b.alloc_qubits(sw)
        uw = interp.get('update_width', c.w2); mask = (1 << uw) - 1
        packed = [((base & mask) | (tabs[a // 128, a % 128][0] & ~mask)) | (s << c.w2)
                  for a, (base, s) in enumerate(interp['rows'])]
        _adaptive_lookup(b, address, km.array(list(c2) + list(step)), packed)
        for i in range(interp['remainder_bits']):
            sh = interp['fraction_bits'] - i
            if sh >= 0: a = step[sh:]; t = c2[:uw]; cin = step[sh - 1] if sh else None
            else: a = step; t = c2[-sh:uw]; cin = None
            b.cx(x[14 + i], t); _folded_gadd(b, a, t, cin); b.cx(x[14 + i], t)
        step_masks.extend(_demolish(b, step)); b.free(step)

    def erase_curvature():
        nonlocal c2
        mm = _demolish(b, c2); b.free(c2); c2 = None
        return mm

    def inner(inverse):
        rows = c.rrow_list()
        if inverse: rows = rows[::-1]
        for i in rows:
            sh = c.sh2[i]
            if sh >= 0: a = c2[sh:]; t = res; cin = c2[sh - 1] if sh else None
            else: a = c2; t = res[-sh:]; cin = None
            b.cx(delta[i], t); _folded_gadd(b, a, t, cin, sub=inverse); b.cx(delta[i], t)

    def outer(inverse):
        derivative = res[:sp['block']] + coarse
        for i in (range(14) if inverse else reversed(range(14))):
            sh = c.sh1[i]
            if sh >= 0: a = derivative[sh:]; t = low; cin = derivative[sh - 1] if sh else None
            else: a = derivative; t = low[-sh:]; cin = None
            b.cx(delta[i], t); _folded_gadd(b, a, t, cin, sub=inverse); b.cx(delta[i], t)

    # Main cycle: compute -> demolish -> phase -> uncompute -> shared repair
    _anf_lookup(b, address, full, ft)
    phase(high, lay['S'])
    bits = _demolish(b, high); b.free(high)

    load_curvature(); inner(False); cm1 = erase_curvature()
    _folded_gadd(b, res[sp['block']:], coarse)
    outer(False)
    phase(low[c.gy:], c.gy)
    outer(True)
    _folded_gadd(b, res[sp['block']:], coarse, sub=True)
    load_curvature(); inner(True); cm2 = erase_curvature()

    bits += _demolish(b, rest); b.free(rest)
    bits += cm1 + cm2
    rtwidth = len(rest); hw = lay['whi']
    repairtable = [
        h | (r << hw) | (tabs[e, a][0] << (hw + rtwidth)) | (tabs[e, a][0] << (hw + rtwidth + c.w2))
        for e in range(2) for a, (h, r) in enumerate(zip(ht[128 * e:128 * (e + 1)], rt[128 * e:128 * (e + 1)]))
    ]
    bits += step_masks; sw = interp['step_width']; off = hw + rtwidth + 2 * c.w2
    for a, (_, step) in enumerate(interp['rows']):
        repairtable[a] |= (step << off) | (step << (off + sw))
    _repair_anf(b, address, repairtable, bits)

    # Un-normalise with a joint top-normalisation repair
    b.cx(x[21], x[0]); b.right_rotate(x[:21], 1, control=x[21]); b.x(x[21])
    pending = None
    for k, amount in reversed(c.NSTAGES[:-1]):
        for i in range(22 - amount): b.cswap(f[k], x[i], x[i + amount])
        top = x[22 - amount:22]; m = b.alloc_bits(1)[0]; b.hmr(f[k], m)
        if k == 3:
            pending = m; continue
        if k == 4:
            parity = m; b.cx(pending, parity)
            b.push_condition(parity)
            top16 = list(reversed(x[6:22])); b.x(top16); anc = b.alloc_qubits(14)
            b.init_and(top16[0], top16[1], anc[0])
            for j in range(1, 14): b.init_and(anc[j - 1], top16[j + 1], anc[j])
            b.push_condition(pending); b.z(anc[6]); b.pop_condition()
            b.cz(anc[13], top16[15])
            for j in reversed(range(1, 14)): b.del_and(anc[j - 1], top16[j + 1], anc[j])
            b.del_and(top16[0], top16[1], anc[0]); b.free(anc); b.x(top16); b.pop_condition()
            b.x(parity); b.push_condition(parity); b.push_condition(pending)
            top8 = x[14:22]; b.x(top8); _phase_all(b, list(top8)); b.x(top8)
            b.pop_condition(); b.pop_condition()
            b.free(pending); b.free(m)
        else:
            b.push_condition(m); b.x(top); _phase_all(b, list(top)); b.x(top); b.pop_condition(); b.free(m)
    b.free(flags)

    return b.finish_circuit()
