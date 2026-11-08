import importlib.util,json
from pathlib import Path
checks=0
for m in range(5,80):
 w=m.bit_length(); mask=(1<<w)-1
 for x in range(m+1):
  reflected=((x^mask)+m+1)&mask
  assert reflected==m-x
  assert (((reflected-m-1)&mask)^mask)==x
  for i in range(m):
   assert (reflected<=i)==(x>=m-i)
   assert (1^(x<=i))==(x>=i+1)
   checks+=2
 for x in range(m-1):
  for i in range(1,m):
   k=m-i+1
   assert (1^(x<k))==(x>=k)
   assert (x+1<k)==(x<m-i)
   checks+=2
 for order in [range(m),range(m-1,-1,-1)]:
  for x in range(m+1):
   prev=None; prefix=0
   for i in order:
    if prev is None:prefix=int(x<=i)
    else:prefix^=int(x==min(prev,i)+1)
    assert prefix==int(x<=i)
    prev=i;checks+=1
p=Path('src/dqi/DQI-10/solution.py')
spec=importlib.util.spec_from_file_location('candidate',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
assert mod.default_n_iters(70)==222
c=mod.build_reference_circuit(15,4,4)
report={'predicate_assertions':checks,'metadata_array_lengths_tested':list(range(5,80)),'directions':['forward','adjoint'],'small_compile':{'m':15,'n':4,'degree':4,'num_qubits':c.num_qubits,'toffoli_like':c.operation_statistics().num_toffoli_like},'limitations':'Algebraic predicate checks and compilation only; no verifier or simulation grading was run.'}
Path('artifacts/dqi/DQI-10/_local_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
