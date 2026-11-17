# Analysis and reconstruction plan: invsqrt_x2763

Input sha256: 47b318383a03c52e08a5c222c5600fd52e004b468f53fad038082fc0f26386ef.

## Direct observations
- Single x register q0..q21, 44 total qubits, 200369 input bytes.
- Both direct KMB serialization and KMX roundtrip are byte-exact (roundtrip.json).
- KMX has 24155 lines including 23 register declarations. Line numbers below include declarations.
- Lines 1..1635 are identical to INV-66 target e46d90...; the INV-66 raw construction records put normalized/root cuts at operations 605/1634, but those raw coordinates must NOT be blindly used for a postprocessed KMX. The exact-prefix observation supports shared normalization/root implementation; final boundary still requires semantic matching.
- Generic/Clifford Z_POW instructions at lines 232..236 and 7592..8168. First group belongs to normalization shared with INV-66; second is the principal phase region. There are 39 total Z_POW instructions. Angles remain exact decimal strings convertible to rational half-turns.
- Tail contains wire permutations to restore x; last instruction SWAP q34 q21. HMR, classical conditions and bit inversions must be preserved in order.
- 1379 CCX, 9 CCZ, 145 CSWAP, 1236 HMR. These are static counts, not executed-shot costs.

## Inferences requiring verification
Shared consumed-root arithmetic is likely, but identical prefix does not establish identical lookup, interpolation, seed, division or phase coefficients. Q44 cannot be obtained by merely deleting two INV-66 wires; changed allocation and nonlinear/phase instructions require explicit recovery.

## Plan
1. Recover explicit Python construction preserving every opcode, rational angle, register and classical condition. Retain a gate-level level label until arithmetic is independently recovered. No runtime reads of original KMB/KMX or embedded tape.
2. Map normalization/root helpers from the tracked INV-51 source, recovering owner coordinates via symbolic emulation. Verify each replaced block instruction-for-instruction before accepting it.
3. Recover coefficient lookup truth tables, address framing, rounding and arithmetic recurrence; record independent classical snapshots. Recover divider/phase/inverse and HMR debt repayment separately.
4. Push source/config/dependencies and build entry point from clean GitHub checkout with a fresh pinned venv, cwd outside checkout and audited reads. Compare bytes against original only in a separate checker. Exact output is necessary, not proof of arithmetic recovery.
5. Record source/config/build hashes in build_only. No new verifier run without the explicitly assigned grading stage; user metrics remain external claims.
6. Postprocessing: inspect existing dead-write HMR/CZ and affine/phase methods read-only first. The original artifact may already contain these, so establish its actual pipeline before proposing an independently validated PP. Do not stack PP or claim benefit from static counts.

## Candidate improvements, not selected or implemented
A. Reduce live-owner peak by phase-aware scheduling around lookup/seed/product; 44 vs 46 supports investigating scheduling, but does not prove mechanism. Reject if debt/phase restoration fails or full Q*C does not improve. Bound to one proven scheduling change after exact reconstruction.
B. Search remaining CCX whose target is measured in X before any value-sensitive read; replace with early HMR plus outcome-conditioned CZ only under all owner/control stability guards. Existing INV-66 method provides a reference. Reject if no eligible gates or semantic guard fails. Test method alone on original bytes; account for cost metric and all measurement branches.
C. Merge Z_POW only when symbolic Boolean features are identical and fixed-point angles are combined exactly. Reject if features differ, condition scope changes or synthesis cost/accuracy fails. Additional rotation count alone is not a benefit estimate.

Stop rather than relabel an opcode emitter as an arithmetic generator. Missing upstream source/search history is a stated limitation, not a reason to read external build data. Preserve Syed Asad Ali attribution and derivative lineage; complete upstream notice/license for this exact file remains unverified.
