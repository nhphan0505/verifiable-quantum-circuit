"""Join a closed norm divisor to the early-N source normalization."""
from types import FunctionType
import inspect
import early_fused_product_companion as schedule
import early_virtual_product_companion as virtual
import adaptive_owned_fused_companion as previous
from owned_fused_companion import finish_scope,OWNER_LOG
from direct_owned_companion import clone
from direct_ratio12 import divide as ratio_divide

source=inspect.getsource(schedule.finish_factory)
first='rgm=inverse_stream_noscratch(b,g);rrm=scale_defer(b,r,g);rim=inverse_stream_noscratch(b,g)'
second='b.cz(g,rgm);b.free(rgm);ar.phase_product(b,r,g,rrm);b.free(rrm)'
third='merged_chart(b,r,F);ar.phase_product(b,g,r,rim);b.free(rim);merged_chart(b,r,F,True)'
assert all(source.count(x)==1 for x in(first,second,third))
source=source.replace(first,'ratio_divide(b,r,g)').replace(second,'').replace(third,'')
scope=dict(schedule.finish_factory.__globals__,ratio_divide=ratio_divide)
exec(compile(source,__file__,'exec'),scope)
plain_factory=scope['finish_factory']


def finish_factory(reference,node_scope):
    owned,owner=finish_scope(node_scope['finish_fused'])
    helpers={name:owned[name]for name in('ar','merged_chart','scale_defer','inverse_stream_noscratch',
                                      'linear_inverse_character','phase_inverse36_pivot')if name in owned}
    ratio=clone(ratio_divide,dict(ratio_divide.__globals__,**helpers))
    mul=clone(virtual.multiply_pair_and_restore,dict(virtual.multiply_pair_and_restore.__globals__,**helpers))
    factory=clone(plain_factory,dict(plain_factory.__globals__,**helpers,ratio_divide=ratio,multiply_pair_and_restore=mul))
    return factory(reference,node_scope)


normalize_first=previous.normalize_first
install=clone(previous.install,dict(previous.install.__globals__,finish_factory=finish_factory))
