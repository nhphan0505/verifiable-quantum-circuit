"""Three-frame forward return in the pre-aligned middle basis.

The whole quotient-head actions are hoisted in their original order.
A prefix of the existing middle aligned route moves before the low dots;
its last pivot edge is restored just across the bottom scalar operation.
Every correlation and product measurement is repaid before its sources move.
"""

def install(cv, scalar, retire_root=True):
    scope = scalar.scope_of(cv)
    short = dict(zip(cv.__code__.co_freevars, cv.__closure__))['core'].cell_contents.__globals__
    dk, ar = scope['dk'], scope['ar']
    original_solve, original_post = scope['look_solve'], scope['direct_post']
    original_dot = dk.selected_dot
    active = []
    phases = []
    pre_frames = {}
    original_partial = scope['pre_partial']
    original_aligned = scope['aligned']
    original_root_pre = short['root_pre_partial']
    original_root_action = short['root_action']
    TOP = 17
    CUT = TOP - 3

    def corr(b, v, c, count):
        out = [b.alloc_qubits(12) for _ in range(count)]
        N = len(c) + count - 1
        V, W = dk.k.vandermonde(N)
        for t in range(N):
            ac = [W[i][t] for i in range(len(v))]
            if any(ac):
                dk.rank_update(b, v, ac, c, V[t][:len(c)], out, V[t][:count])
        return out






    def select_copy(b, x, y, target, F):
        b.cx(x, target); b.cx(x, y)
        for u, v in zip(y, target): b.ccx(F, u, v)
        b.cx(x, y)

    def select_phase(b, x, y, mask, F):
        b.cz(x, mask); b.cx(x, y)
        for u, v in zip(y, mask): b.ccz(F, u, v)
        b.cx(x, y)

    def retire_one(b, v, c, word, count, index):
        r = b.alloc_bits(12); b.hmr(word, r); b.free(word)
        N = len(c) + count - 1
        V, W = dk.k.vandermonde(N)
        field = ar.field(12)
        for t in range(N):
            ac = [W[i][t] for i in range(len(v))]
            if not any(ac): continue
            mask = b.alloc_bits(12); b.bit_store(mask, False)
            for bit in range(12):
                for i in ar.bits(field.mul(V[t][index], 1 << bit)):
                    b.cx(r[i], mask[bit])
            x, xp = dk.k.expose(b, v, ac)
            cc = V[t][:len(c)]
            y, yp = dk.k.expose(b, c, cc)
            ar.phase_product(b, x, y, mask)
            dk.k.unexpose(b, c, cc, yp); dk.k.unexpose(b, v, ac, xp)
            b.free(mask)
        b.free(r)


    def flag_copy(b, F, x, out, complement=False):
        if complement: b.x(F)
        for u, v in zip(x, out): b.ccx(F, u, v)
        if complement: b.x(F)

    def fused(b, f, g, payloads, F2, phase):
        f0, g0, v0, parent0 = phase[f'_a16_{TOP}_forward_block']
        f1 = g0
        assert len(f0)-1 == TOP and len(f1)-1 == TOP-1
        assert f == f0[:-2]
        # The special child quotient uses the reconstructed root inverse.
        Fchild = phase['returned_gap'][16]
        # The special child formula reads this selected-pivot edge.
        b.cswap(Fchild, f1[-3], f0[-4])
        R = restore_root_keep(b, f1, f0[:-2], Fchild, F2, phase)
        r_early=b.alloc_bits(12); b.hmr(R,r_early); b.free(R)
        parent1 = ([row[-1] for row in v0], f0[-1], f0[-2])
        phase['_child_scalar_context'] = (f0[:-2], Fchild, F2)
        try:
            prior_qpost(b, f1[-1], [row[:-1] for row in v0], None,
                        16, parent1, phase=phase)
        finally:
            del phase['_child_scalar_context']
        phase[f'_a16_{TOP}_hoisted'] = {16}
        R=root_pivot(b,f1,f0[:-2],Fchild,F2,phase['returned_gap'][17])
        b.cz(R,r_early); b.free(r_early)
        # Hoist the root's multiply before its dot. R is the exact clipped
        # root pivot, and f0[-1] is its reconstructed inverse.
        for row in v0:
            short['old'].scale(b, row[-1], R, f0[-1], False)
        rm = b.alloc_bits(12); b.hmr(R, rm); b.free(R)
        phase['_root_pivot_debt'] = rm
        if retire_root:
            mask = b.alloc_bits(12); b.hmr(f0[-1], mask); b.free(f0[-1])
            phase['_a22_root_inverse_return'] = (f0[-1], mask)
        F0 = phase['returned_gap'][TOP]
        F1 = phase['returned_gap'][TOP-1]
        q0, q1 = f1[-2:]
        # Undo the low prefix of the middle aligned route. The original
        # parent return later performs only its remaining suffix.
        with b.mark('aligned_route'):
            for x, y in zip(f[:CUT], g[:CUT]): b.cswap(F1, x, y)
        phase[f'_a16_{TOP}_prefix_route'] = F1
        for j, v in enumerate(payloads):
            low = v[:CUT]
            heads = [v0[j][-1], v0[j][-2], v0[j][-3]]
            fs = corr(b, low, f[:CUT], 3)
            # d0 = (1+F0)*q0*d1 + q1*e + (1+F0)*G0 + F0*F1corr.
            b.cswap(F1, fs[1], fs[2])
            ar.mul_xor0(b, q1, fs[1], heads[0])
            b.cswap(F1, fs[1], fs[2])
            flag_copy(b, F0, fs[1], heads[0])
            retire_one(b, low, f[:CUT], fs[2], 3, 2)
            b.cswap(F1, fs[0], fs[1])
            b.cx(fs[0], heads[1])
            product = b.alloc_qubits(12)
            ar.mul_xor0(b, q0, fs[0], product)
            flag_copy(b, F0, product, heads[0], True)
            rm = b.alloc_bits(12); b.hmr(product, rm); b.free(product)
            ar.phase_product(b, q0, fs[0], rm); b.free(rm)
            b.cswap(F1, fs[0], fs[1])
            temp = b.alloc_qubits(12)
            select_copy(b, fs[0], fs[1], temp, F2)
            flag_copy(b, F1, temp, heads[2])
            rm = b.alloc_bits(12); b.hmr(temp, rm); b.free(temp)
            select_phase(b, fs[0], fs[1], rm, F2); b.free(rm)
            retire_one(b, low, f[:CUT], fs[0], 3, 0)
            retire_one(b, low, f[:CUT], fs[1], 3, 1)

            gs = corr(b, low, g[:CUT], 2)
            flag_copy(b, F0, gs[0], heads[0], True)
            temp = b.alloc_qubits(12)
            select_copy(b, gs[0], gs[1], temp, F2)
            flag_copy(b, F1, temp, heads[2], True)
            rm = b.alloc_bits(12); b.hmr(temp, rm); b.free(temp)
            select_phase(b, gs[0], gs[1], rm, F2); b.free(rm)
            retire_one(b, low, g[:CUT], gs[0], 2, 0)
            retire_one(b, low, g[:CUT], gs[1], 2, 1)

    def bottom_post(b, f, g, payloads, F, H, parent, incoming, defer, phase):
        m = len(f)-1
        assert m == TOP-2 and defer
        scope['q_post'](b, f[-1], payloads, H, m, parent, phase=phase)
        # Retire the one-bit zero predicate across the three-word pass.
        # Recreate it with the ordinary inverse producer and repay its X debt.
        scope['pivot'](b, g, F); a = g[-1]
        # Keep the explicit strip for the parameterized public prefix.
        for i in range(CUT, len(g)-1):
            with dk.selected(b, g[i], g[i-1], F) as coefficient:
                for v in payloads: ar.mul_xor0(b, coefficient, v[i], v[-1])
        Z0 = scope['fresh_zero_flag'](b, a)
        b.cx(Z0, a[0]); scope['pivot'](b, g, F)
        phase['heads'][m] = scope['high_full_restore'](b, f, g, F)
        b.cx(Z0, g[-2][0])
        zm0 = b.alloc_bits(1); b.hmr(Z0, zm0[0]); b.free(Z0)
        fused(b, f, g, payloads, F, phase)
        # Restore only the pivot edge while its scalar inverse is consumed.
        # All correlation characters have already been repaid in the new basis.
        middle_gap = phase['returned_gap'][TOP-1]
        b.cswap(middle_gap, f[CUT-1], g[CUT-1])
        b.cswap(middle_gap, f[-2], g[-1])
        scope['pivot'](b, g, F); a = g[-1]
        ai, Z = scope['inverse_zero'](b, a)
        b.cz(Z, zm0[0]); b.free(zm0)
        scope['consume'](b, ai, Z, incoming)
        b.cx(Z, a[0]); b.cx(Z, ai[0])
        for v in payloads: scope['scale'](b, v[-1], a, ai, True)
        b.cx(Z, ai[0]); r = b.alloc_bits(12); b.hmr(ai, r); b.free(ai)
        b.cx(Z, a[0]); scope['pivot'](b, g, F)
        b.cswap(middle_gap, f[CUT-1], g[CUT-1])
        b.cswap(middle_gap, f[-2], g[-1])
        zm = b.alloc_bits(1); b.hmr(Z, zm[0]); b.free(Z)
        return r, zm

    def selected_dot(b, g, v, target, F):
        if not active or active[-1]['m'] not in (TOP, TOP-1):
            return original_dot(b, g, v, target, F)
        frame = active[-1]
        if frame['done']: return
        frame['done'] = True
        for i in range(CUT, len(g)):
            with dk.selected(b, g[i], g[i-1], F) as c:
                for row in frame['payloads']:
                    ar.mul_xor0(b, c, row[i], row[-1])

    prior_qpost = scope['q_post']
    def q_post(b, q, payloads, H, m, parent, reverse=False, phase=None):
        if not reverse and m in phase.get(f'_a16_{TOP}_hoisted', ()):
            phase[f'_a16_{TOP}_hoisted'].remove(m)
            return
        return prior_qpost(b, q, payloads, H, m, parent, reverse, phase)

    def post(b, f, g, payloads, F, H, parent, reverse=False,
             incoming=None, defer=False, phase=None):
        m = len(f)-1
        if reverse or m not in (TOP, TOP-1, TOP-2) or f'_a16_{TOP}_forward_block' not in phase:
            return original_post(b, f, g, payloads, F, H, parent,
                                 reverse, incoming, defer, phase)
        if m == TOP-2:
            return bottom_post(b, f, g, payloads, F, H, parent, incoming, defer, phase)
        active.append(dict(m=m, payloads=payloads, done=False))
        try:
            result = original_post(b, f, g, payloads, F, H, parent,
                                   reverse, incoming, defer, phase)
            return result
        finally:
            active.pop()

    def aligned(b, f, g, F):
        if phases and len(f)-1 == TOP-1 and f'_a16_{TOP}_prefix_route' in phases[-1]:
            assert phases[-1].pop(f'_a16_{TOP}_prefix_route') == F
            with b.mark('aligned_route'):
                for x, y in zip(f[:-2][CUT+1:], g[:-1][CUT+1:]): b.cswap(F, x, y)
            return
        return original_aligned(b, f, g, F)

    def root_pivot(b,f,g,Fchild,K,Froot):
        q=f[-1]
        R = b.alloc_qubits(12)
        scope['pivot'](b, g, Fchild)
        b.ccx(Fchild, K, g[-1][0])
        ar.mul_xor0(b, q, g[-1], R)
        b.ccx(Fchild, K, g[-1][0])
        scope['pivot'](b, g, Fchild)
        for x, y in zip(g[-1], R): b.ccx(Froot, x, y)
        b.ccx(Froot, Fchild, R[0])
        return R

    def restore_root_keep(b, f, g, Fchild, K, phase):
        held, mask = phase.pop('_ephemeral_root')
        q = f[-1]
        Froot = scope['fresh_zero_flag'](b, q)
        R = root_pivot(b,f,g,Fchild,K,Froot)
        phase['_root_early_flag'] = Froot
        replacement = scope['inverse_initialized'](b, R)
        held[:] = replacement
        b.cz(held, mask); b.free(mask)
        return R

    def root_pre(b, f, g, payloads, ai, Z, F):
        root_frames.append((f,g,payloads))
        return original_root_pre(b,f,g,payloads,ai,Z,F)

    root_frames=[]
    def partial(b, f, g, payloads, F, cutoff, defer_coefficient=False):
        if len(f)-1 == 16 and root_frames:
            rf,rg,rv=root_frames.pop()
            phases[-1][f'_a16_{TOP}_forward_block']=(rf,rg,rv,None)
        return original_partial(b,f,g,payloads,F,cutoff,defer_coefficient)

    def root_action(b,f,g,payloads,ai,Z,F,post,undo):
        if not (post and not undo and root_phases and
                f'_a16_{TOP}_forward_block' in root_phases[-1]):
            return original_root_action(b,f,g,payloads,ai,Z,F,post,undo)
        phase=root_phases[-1]
        assert Z is False
        if retire_root:
            saved,mask=phase.pop('_a22_root_inverse_return')
            replacement=scope['inverse_initialized'](b,g[-1])
            saved[:]=replacement
            b.cz(ai,mask); b.free(mask)
        for i in range(CUT,len(g)-1):
            with dk.selected(b,g[i],g[i-1],F) as c:
                for row in payloads: ar.mul_xor0(b,c,row[i],row[-1])
        for row in payloads: short['old'].scale(b,row[-1],g[-1],ai,True)
        short['root_restore'](b,f,g,ai,F)
        del phase[f'_a16_{TOP}_forward_block']
        assert not phase.pop(f'_a16_{TOP}_hoisted')

    root_phases=[]
    original_root=short['look_root_cached']
    def root(b,O,g,payloads,reverse,phase):
        root_phases.append(phase)
        try:return original_root(b,O,g,payloads,reverse,phase)
        finally:root_phases.pop()

    def solve(b, f, g, payloads, H=None, parent=None, reverse=False, phase=None):
        phases.append(phase)
        try:
            return original_solve(b, f, g, payloads, H, parent, reverse, phase)
        finally:
            phases.pop()

    short['root_pre_partial'] = root_pre
    short['root_action'] = root_action
    short['look_root_cached'] = root
    scope['aligned'] = aligned
    short['aligned'] = aligned
    scope['pre_partial'] = partial
    scope['look_solve'] = solve
    short['old'].look_solve = solve
    scope['direct_post'] = post
    scope['q_post'] = q_post
    dk.selected_dot = selected_dot
    return cv
