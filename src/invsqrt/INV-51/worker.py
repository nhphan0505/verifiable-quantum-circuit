"""Execute one integrated compiler stage and record its source/data reads.

Kickmix is loaded from the pinned Windows virtualenv. Source components have no
Unix resource imports or calls at import time. This worker adds no circuit rewrite
or source patch. A standard Python audit hook records filesystem dependencies for
independent clean-build checks; it does not fabricate hashes or replace file data.
"""
from pathlib import Path
import json
import runpy
import sys


def main():
    if len(sys.argv)<5 or sys.argv[1]!='--trace':
        raise SystemExit('worker.py --trace FILE SCRIPT [ARGS...]')
    trace=Path(sys.argv[2]).resolve()
    script=Path(sys.argv[3]).resolve()
    reads=set()

    def audit(event, args):
        if event!='open' or not isinstance(args[0],(str,bytes)):
            return
        mode=args[1]
        if mode is None or (isinstance(mode,str) and 'r' in mode):
            reads.add(str(Path(args[0]).resolve()))

    sys.addaudithook(audit)
    import kickmix
    print(json.dumps({'kickmix':kickmix.__file__,'input_script':str(script)}),flush=True)
    sys.argv=[str(script),*sys.argv[4:]]
    sys.path.insert(0,str(script.parent))
    try:
        runpy.run_path(str(script),run_name='__main__')
    finally:
        trace.write_text(json.dumps(sorted(reads),indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
