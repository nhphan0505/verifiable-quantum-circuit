"""Load the tracked INV-51 arithmetic/compiler as a shared helper library.

No INV-51 generator, table loader, gate replay, or solution entry point is run.
Only normalization/root, generic carry arithmetic, balanced division and its
typed Boolean restoration helpers are selected. Compatibility math constants
come from this experiment's small declared JSON, not the INV-51 bundle.
"""
from pathlib import Path
import importlib.util
import json
import sys
HERE = Path(__file__).resolve().parent

def load_backend():
    path = HERE.parent / 'INV-51/circuit.py'
    spec = importlib.util.spec_from_file_location('_inv66_shared_arithmetic', path)
    source = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = source
    spec.loader.exec_module(source)
    source._TABLES = json.loads((HERE / 'data/arithmetic_helpers.json').read_text(encoding='utf-8'))
    return source

def load_math():
    source = load_backend()
    spec = source._Spec('inv66_arithmetic_context', source._VROOT / 'tools/build_variant.py')
    module = source._new_module(spec)
    spec.loader.exec_module(module)
    variant = source._import_component('arithmetic_variant', 'tools/build_variant.py', False)
    components = dict(variant.install())
    old = variant.old
    common = old.common
    ctx = module.Context()
    ctx.variant, ctx.old, ctx.components, ctx.common, ctx.km = (variant, old, components, common, common.km)
    ctx.baseline = components['lifecycle'].baseline
    ctx.tables = old.local_module('tables07')
    ctx.phase = old.local_module('phase07')
    ctx.base = old.load_baseline('generate')
    ctx.gate = variant.accepted_gate()
    for name in ('patch_fwd_narrow.py', 'patch_endpoint_v9e2.py', 'patch_hret_sat_s15k7a.py', 'patch_proddisp.py'):
        module.load_patch(source._VROOT / 'patches' / name).apply(ctx)
    module.load_patch(source._VROOT / 'patches/patch_seedinv.py')
    ctx.normalization = components['normalization']
    ctx.root = components['root']
    ctx.divider = ctx.old.divider
    ctx.codebook = ctx.tables.cb

    def inverse_product(builder, v, D, word, token, dirty):
        return source._patch_seedinv_product_inverse(builder, v, D, word, token, dirty, baseline=ctx.baseline)
    ctx.inverse_product = inverse_product
    ctx.inverse_seed = source._patch_seedinv_make_seed_cleanup(ctx.baseline)
    return (source, ctx)
