"""Exact substitutions on the frozen narrow240 decoder (isolated port)."""
from pathlib import Path
import sys
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import decode_retimed as base
import exact_subs as xsub
from exp.arithmetic.lowwidth import phase_inverse_generic6
from phase_quantum import phase_inverse6_9

replacements = {
    id(xsub.core.external_chain_step): xsub.chain_step,
    id(xsub.old6): xsub.phase_inverse6_quad4,
    id(xsub.old_generic6): xsub.phase_inverse6_quad4,
    id(phase_inverse6_9): xsub.phase_inverse6_quad4,
    id(xsub.old12): xsub.phase_inverse12_virtual,
    id(xsub.zero1.inverse_zero): xsub.inverse_zero,
    id(xsub.joint.inverse_zero): xsub.inverse_zero,
    id(xsub.joint.inverse6_init19): xsub.initialized19,
    id(xsub.iso.inverse6_xor20): xsub.initialized_only(xsub.iso.inverse6_xor20),
    id(xsub.ref.inverse6_xor20): xsub.initialized_only(xsub.ref.inverse6_xor20),
}
decode = xsub.private_rebind(base.decode, replacements)
