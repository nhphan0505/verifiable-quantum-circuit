"""Preserve the input decoder's actual scalar-stream implementation."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'root')]
import decode_trailing_companion as companion
import decode_trailing_normcache as cached


def install(entry,with_norm=True,ceiling=889):
    original=entry.__globals__['extraction']
    ref=original.__globals__['ref']
    current_stream=ref.external_normalize_paired.__globals__['inverse_stream_noscratch']
    result=cached.install(entry,ceiling) if with_norm else companion.install(entry)
    extraction=result.__globals__['extraction']
    scope=dict(extraction.__globals__)
    scope['inverse_stream_noscratch']=current_stream
    character=scope['linear_inverse_character']
    scope['linear_inverse_character']=companion.combo.xsub.clone(character,
        dict(character.__globals__,inverse_stream_noscratch=current_stream))
    if with_norm:
        replacements=dict(companion.combo.synth.replacements)
        replacements[id(cached.ns.inverse_stream_noscratch)]=current_stream
        inverse=companion.combo.xsub.private_rebind(cached.inverse12_keep_norm,replacements)
        def consume(b,x):return inverse(b,x,ceiling)
        scope['inverse12_keep_norm']=consume
    extraction=companion.combo.xsub.clone(extraction,scope)
    return companion.combo.xsub.clone(result,dict(result.__globals__,extraction=extraction))


decode=install(companion.combo.decode)
