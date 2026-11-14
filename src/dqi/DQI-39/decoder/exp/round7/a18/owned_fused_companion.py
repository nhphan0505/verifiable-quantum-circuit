"""Keep actual private arithmetic owners inside the new complete stage."""
from types import FunctionType
import early_fused_product_companion as implementation
import early_virtual_product_companion as virtual
from direct_owned_companion import clone

OWNER_LOG=[]


def finish_scope(fn):
    pending=[fn];seen=set()
    while pending:
        current=pending.pop(0)
        if id(current)in seen:continue
        seen.add(id(current))
        if 'linear_inverse_character' in current.__code__.co_names:
            return current.__globals__,current
        for cell in current.__closure__ or():
            value=cell.cell_contents
            if isinstance(value,FunctionType):pending.append(value)
    raise AssertionError(('actual finisher arithmetic scope not found',fn.__code__.co_filename))


def finish_factory(reference,node_scope):
    owned,owner=finish_scope(node_scope['finish_fused'])
    helpers={name:owned[name]for name in ('ar','merged_chart','scale_defer','inverse_stream_noscratch',
                                         'linear_inverse_character','phase_inverse36_pivot')if name in owned}
    required={'ar','merged_chart','scale_defer','inverse_stream_noscratch','linear_inverse_character'}
    assert required<=helpers.keys()
    multiplier=clone(virtual.multiply_pair_and_restore,dict(virtual.multiply_pair_and_restore.__globals__,**helpers))
    factory=clone(implementation.finish_factory,dict(implementation.finish_factory.__globals__,**helpers,
                                                   multiply_pair_and_restore=multiplier))
    OWNER_LOG.append(dict(owner_file=owner.__code__.co_filename,owner_name=owner.__name__,
                          helpers={k:(v.__code__.co_filename,v.__name__)for k,v in helpers.items()if isinstance(v,FunctionType)}))
    return factory(reference,node_scope)


normalize_first=implementation.normalize_first
install=clone(implementation.install,dict(implementation.install.__globals__,finish_factory=finish_factory))
