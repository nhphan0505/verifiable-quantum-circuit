"""Run frozen author generator modules in the repository Windows virtualenv.

Only Unix resource API compatibility is supplied. setrlimit requests are logged,
not represented as enforced limits; solution.py enforces subprocess timeouts.
No source/hash/assertion, circuit operation, phase or verifier is altered.
This launcher is for build modules, not the author's guarded grading programs.
Kickmix is preloaded from the pinned pip environment, never the Linux .so.
"""
from pathlib import Path
import json
import os
import runpy
import sys
import types


def main():
    if os.name != 'nt':
        raise RuntimeError('This adapter is specifically for Windows .venv')
    if len(sys.argv) < 2:
        raise SystemExit('usage: windows_runner.py SCRIPT [ARGS...]')
    import kickmix
    print(json.dumps({'windows_kickmix': kickmix.__file__, 'unix_rlimits_enforced': False}), flush=True)
    shim = types.ModuleType('resource')
    shim.RLIMIT_AS = 9
    shim.RLIMIT_CORE = 4
    shim.RLIMIT_DATA = 2
    shim.RLIM_INFINITY = -1

    def setrlimit(which, limits):
        if which not in (shim.RLIMIT_AS, shim.RLIMIT_CORE, shim.RLIMIT_DATA):
            raise NotImplementedError(f'Unsupported resource request: {which}')
        print(json.dumps({'unix_resource_request': which, 'limits': limits,
                          'enforced': False, 'reason': 'Windows build compatibility'}), flush=True)

    shim.setrlimit = setrlimit
    sys.modules['resource'] = shim
    script = Path(sys.argv[1]).resolve()
    sys.argv = [str(script), *sys.argv[2:]]
    sys.path.insert(0, str(script.parent))
    runpy.run_path(str(script), run_name='__main__')


if __name__ == '__main__':
    main()
