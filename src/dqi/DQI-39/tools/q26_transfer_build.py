"""Reviewed source-only q26 carry experiments, with unchanged raw hash control.

Public arithmetic/carry: SomeJointV25, yoyobar, Ali Haydar Ozdag and upstream.
Own contribution: portable construction, exact retained-boundary comparison,
and optional pole-recurrence diagnostic. No native input or network is used.
"""
import argparse
import ast
import builtins
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / 'repair'


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(p, x):
    Path(p).write_text(json.dumps(x, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def install_retention(entry, source, cuts, selected, debug, debug_flags):
    import walk_bound
    functions=walk_bound.functions(entry)
    policy_edits=[]
    for scope in {id(fn.__globals__):fn.__globals__ for fn in functions}.values():
        for key in ('EXTERNAL_HOMOGENEOUS','SELECT'):
            if scope.get(key)==frozenset(range(5,17)):
                scope[key]=frozenset(selected);policy_edits.append(key)
    assert policy_edits
    ordered=sorted(selected);cuts=set(cuts)
    # A gap in the selected policy necessarily ends a carry block.
    cuts.update(g for i,g in enumerate(ordered) if i==len(ordered)-1 or ordered[i+1]!=g+1)
    assert cuts <= set(selected) and ordered[-1] in cuts
    starts=set();first=ordered[0];starts.add(first)
    for i,g in enumerate(ordered[:-1]):
        if g in cuts:starts.add(ordered[i+1])
    bank={}; counts=dict(forward=0,reverse=0,predictions=0,debug_relations=0)
    if debug:
        sys.path.insert(0,str(PARENT))
        from gap3_completion import zero_toggle

    def forward(b,token,gi):
        state=bank.setdefault(id(b),dict(masks={},held={},flag=None))
        pole=token.pop('pole');counts['forward']+=1
        if gi in cuts:state['held'][gi]=pole
        else:
            mask=b.alloc_bits(1);b.hmr(pole,mask[0]);b.free(pole);state['masks'][gi]=mask

    def pole_at(b,gi):
        state=bank[id(b)];counts['reverse']+=1
        if gi in cuts:
            assert state['flag'] is None,(gi,'carry crossed retained boundary')
            state['flag']=state['held'].pop(gi)
        else:
            mask=state['masks'].pop(gi);b.cz(state['flag'],mask[0]);b.free(mask)
        assert state['flag'] is not None
        return state['flag']

    def next_pole(b,pole,marker,gi,zero_flag):
        state=bank[id(b)]
        if debug and gi-1 in selected:
            assert cuts==set(selected),'Diagnostic requires exact all-held control'
            b.x(pole);zero_toggle(b,list(marker)+[pole],debug_flags[gi-1]);b.x(pole)
            b.cx(state['held'][gi-1],debug_flags[gi-1]);counts['debug_relations']+=1
        if gi in starts:
            state['flag']=None
            if gi==ordered[0]:assert not state['held'] and not state['masks']
            return
        b.x(pole);state['flag']=zero_flag(b,list(marker)+[pole]);b.x(pole)
        counts['predictions']+=1

    changed=0
    for fn in functions:
        if fn.__name__=='external_node_chain' and 'carry_pole' in fn.__code__.co_names:
            fn.__globals__.update(carry_forward=forward,carry_pole=pole_at,carry_next=next_pole);changed+=1
    assert changed
    return dict(selected=ordered,cuts=sorted(cuts),starts=sorted(starts),owners=changed,policy_edits=policy_edits,counts=counts)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--mode',choices=['raw','held','mixed','debug'],default='raw')
    p.add_argument('--cuts',default='16');p.add_argument('--no6',action='store_true');p.add_argument('--first-gi',type=int,choices=range(3,8),default=5)
    p.add_argument('--gap3',action='store_true');p.add_argument('--closure-repair',action='store_true');p.add_argument('--stream-repair',action='store_true')
    p.add_argument('--reference-converter',action='store_true');p.add_argument('--inplace-repair',action='store_true');p.add_argument('--inplace-mode',choices=['stream','local'],default='stream');p.add_argument('--lead',action='store_true');p.add_argument('--flag-mbu',action='store_true');p.add_argument('--ceiling',type=int);p.add_argument('--dry-profile',action='store_true');a=p.parse_args();start=time.monotonic()
    packet=a.packet.resolve();out=a.out.resolve();assert not out.exists();out.mkdir(parents=True)
    generator_snapshot=Path(__file__).read_bytes()
    for helper in ('carry_width_select.py','carry_gap3_inplace.py','carry_infinity_lead.py'):
        ast.parse((ROOT/'tools'/helper).read_text(encoding='utf-8'),filename=helper)
    assert not a.closure_repair or a.gap3
    assert not a.stream_repair or a.gap3
    assert not (a.stream_repair and a.closure_repair)
    pin=json.loads((packet/'SOURCE_PACKET.json').read_text())
    assert pin['all_inputs_resolved'] and not pin['missing_inputs']
    for n,h in pin['source_files'].items():assert sha(packet/n)==h,n
    for n,v in pin['input_files'].items():assert sha(packet/n)==v['sha256'],n
    source=packet/'blocks/dqi/carry-q26-892/source'
    # The public ownership matcher uses POSIX filename suffixes. Preserve its
    # assertions and operations while normalizing code metadata on Windows.
    original_compile=builtins.compile
    compatibility=[]
    def portable_compile(text,filename,*args,**kwargs):
        if str(filename).replace('\\','/').endswith('/loader_prune.py') and isinstance(text,(str,bytes)):
            if isinstance(text,bytes):text=text.decode('utf-8')
            old='except (AttributeError, OSError):'
            assert text.count(old)==1
            text=text.replace(old,'except (AttributeError, OSError, TypeError):')
            compatibility.append('loader_prune: treat Windows CDLL(None) TypeError as unavailable Linux malloc_trim; no circuit operation changed')
        return original_compile(text,str(filename).replace('\\','/'),*args,**kwargs)
    builtins.compile=portable_compile
    import kickmix as km
    sys.modules['circ']=km
    def audit(event,args):
        if event in ('subprocess.Popen','os.system','socket.connect','socket.bind'):
            raise RuntimeError('Source constructor attempted external operation: '+event)
        if event=='open' and not isinstance(args[0],int):
            mode=args[1];flags=args[2]
            write=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
            if write:assert Path(args[0]).resolve().is_relative_to(out),('Write outside experiment output',args[0])
        if event in ('os.remove','os.rmdir','os.rename'):
            raise RuntimeError('Source constructor attempted mutation: '+event)
    sys.addaudithook(audit)
    spec=importlib.util.spec_from_file_location('decoder_under_test',source/'decode_carry_round7.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    entry=module.decode;repair=None;converter_isolation=None;width=None
    if a.ceiling is not None:
        from carry_width_select import install
        width=install(entry,source,a.ceiling)
    if a.reference_converter:
        from carry_reference_converter import install as install_converter
        entry,converter_isolation=install_converter(entry,source)
    if a.gap3:
        pm=json.loads((PARENT/'MANIFEST.json').read_text())
        for name in ['gap3_completion.py','gap3_shared_flag.py']:assert sha(PARENT/name)==pm['files'][name]
        sys.path.insert(0,str(PARENT))
        if a.stream_repair:
            from carry_gap3_stream import install
            entry,repair=install(entry,source)
        elif a.closure_repair:
            from carry_gap3_closure import install
            entry,repair=install(entry,source)
        else:
            from gap3_shared_flag import install
            entry,repair=install(entry,source,'local')
    lead=None
    if a.lead:
        from carry_infinity_lead import install
        lead=install(entry,source)
    if a.inplace_repair:
        from carry_gap3_inplace import install
        entry,repair=install(entry,source,a.inplace_mode)
    flag_mbu=None
    if a.flag_mbu:
        from carry_flag_mbu import install
        flag_mbu=install(entry,source)
    if a.dry_profile:
        from dqi_shared_control_products import dry_builder
        b=dry_builder(km)
    else:b=km.CircuitBuilder()
    S=[b.alloc_qubits(12)for _ in range(70)];E=[b.alloc_bits(12)for _ in range(4095)]
    selected=set(range(a.first_gi,17)) - ({6} if a.no6 else set())
    debug_flags={g:b.alloc_qubits(1)[0] for g in sorted(selected) if g<16} if a.mode=='debug' else {}
    carry=None
    if a.mode!='raw':
        cuts=selected if a.mode in ('held','debug') else {int(x)for x in a.cuts.split(',')}
        carry=install_retention(entry,source,cuts,selected,a.mode=='debug',debug_flags)
    else:assert not a.no6
    print(json.dumps(dict(stage='CONSTRUCTING',mode=a.mode,gap3=a.gap3,closure_repair=a.closure_repair,selected=sorted(selected),cuts=carry['cuts'] if carry else None,owners=carry['owners'] if carry else 0)),flush=True)
    profile={}
    def trace(frame,event,arg):
        if event!='call':return
        local=frame.f_locals
        if local.get('b')is not b:return
        f=local.get('f');g=local.get('g')
        if not isinstance(f,(list,tuple))or not isinstance(g,(list,tuple)):return
        key=(frame.f_code.co_name,str(Path(frame.f_code.co_filename).name),len(f),len(g))
        profile[key]=profile.get(key,0)+1
    if a.dry_profile:sys.setprofile(trace)
    try:entry(b,S,E)
    finally:
        if a.dry_profile:sys.setprofile(None)
    if a.dry_profile:
        report=dict(status='ALLOCATOR_AND_ACTUAL_SOLVER_CALLS_ONLY',Q=b.high,source_packet_sha256=sha(packet/'SOURCE_PACKET.json'),
            actual_calls=[dict(name=k[0],file=k[1],f=k[2],g=k[3],calls=v)for k,v in sorted(profile.items())],
            carry=carry,repair=repair,native_circuit_built=False,seconds=time.monotonic()-start)
        save(out/'report.json',report);(out/'generator_source.py').write_bytes(generator_snapshot)
        print(json.dumps(dict(status=report['status'],Q=b.high,call_shapes=len(profile),seconds=report['seconds'])),flush=True)
        return
    metadata=[]
    for i in range(70):
        metadata.append(f'REGISTER r{i} "S{i}"');metadata.extend(f'APPEND_TO_REGISTER q{12*i+k} r{i}'for k in range(12))
    for j in range(4095):
        metadata.append(f'REGISTER r{70+j} "E{j}"');metadata.extend(f'APPEND_TO_REGISTER b{12*j+k} r{70+j}'for k in range(12))
    # Keep the official S/E register schema, even in diagnostics. Debug output
    # wires are explicitly mapped in the report and read as ancillas; they are
    # not a valid submission because they intentionally retain mismatch bits.
    c=km.Circuit('\n'.join(metadata))+b.finish_circuit();target=out/'dqi.kmb';c.to_file(target,format='kmb')
    digest=sha(target)
    if a.mode=='raw' and not a.gap3:assert digest=='b7ca9bce749dcd049f94326446e90cad474b51e6e0abf81561fc37f261abf69b',digest
    report=dict(status='SOURCE_ONLY_CARRY_NATIVE_BUILT',source_packet_sha256=sha(packet/'SOURCE_PACKET.json'),
        mode=a.mode,windows_compile_filenames_posix=True,host_only_compatibility=compatibility,raw_exact_control=(a.mode=='raw'and not a.gap3),
        sha256=digest,Q=c.num_qubits,static_T=int(c.operation_statistics().num_toffoli_like),num_ops=len(c),num_bits=c.num_bits,
        carry=carry,repair=repair,lead=lead,flag_mbu=flag_mbu,width=width,converter_isolation=converter_isolation,debug_qubits={str(g):str(q)for g,q in debug_flags.items()},
        source_only=True,native_inputs=False,public_notebook_orchestration_executed=False,
        inplace_repair_source_sha256=sha(ROOT/'tools/carry_gap3_inplace.py') if a.inplace_repair else None,
        lead_compiler_source_sha256=sha(ROOT/'tools/carry_infinity_lead.py') if a.lead else None,
        flag_mbu_source_sha256=sha(ROOT/'tools/carry_flag_mbu.py') if a.flag_mbu else None,
        native_full_verification=False,seconds=time.monotonic()-start,generator_sha256=hashlib.sha256(generator_snapshot).hexdigest(),kickmix_path=km.__file__,
        closure_repair_source_sha256=sha(ROOT/'tools/carry_gap3_closure.py') if a.closure_repair else None,
        stream_repair_source_sha256=sha(ROOT/'tools/carry_gap3_stream.py') if a.stream_repair else None)
    save(out/'report.json',report);(out/'generator_source.py').write_bytes(generator_snapshot)
    print(json.dumps({k:v for k,v in report.items()if k not in ('repair','carry','lead','flag_mbu','width','converter_isolation')}),flush=True)


if __name__=='__main__':main()
