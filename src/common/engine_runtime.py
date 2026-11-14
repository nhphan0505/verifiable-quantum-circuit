"""Select the native Linux/macOS engine runtime, or bridge Windows to WSL.

Only argument arrays are executed. WSL paths are resolved by wslpath, including
paths with spaces. Engine installation is explicit and failures never fall back.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

VERSION = '0.6.0'


def runtime(root):
    root = Path(root).resolve()
    if sys.platform == 'win32':
        try:
            probe = subprocess.run(['wsl.exe', '--exec', 'true'], capture_output=True)
            if probe.returncode:
                raise OSError('WSL distribution unavailable')
            linux_root = subprocess.check_output(['wsl.exe', '--exec', 'wslpath', '-a', str(root)], text=True).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError('Cài WSL Ubuntu: mở PowerShell Administrator, chạy wsl --install -d Ubuntu, khởi động lại và mở Ubuntu để hoàn tất. Xem docs/LOCAL_GRADING.md.') from exc
        return ['wsl.exe', '--exec', linux_root + '/.venv-engine/bin/python'], linux_root
    if sys.platform not in ('linux', 'darwin'):
        raise RuntimeError('Engine requires Linux/macOS; Windows requires WSL.')
    return [sys.executable], str(root)


def preflight(prefix):
    code = "import sys,json,platform,importlib.metadata as m; from kickmix_engine import kernel_info; print(json.dumps(dict(python=sys.version,platform=platform.platform(),packages={p:m.version(p) for p in ['kickmix','numpy','scipy','kickmix-engine']},kernel=kernel_info())))"
    try:
        info = json.loads(subprocess.check_output(prefix + ['-c', code], text=True, stderr=subprocess.PIPE))
        if info['packages']['kickmix-engine'] != VERSION:
            raise ValueError('engine version mismatch')
        return info
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise RuntimeError('Cài kickmix-engine 0.6.0 trong runtime chấm; xem docs/LOCAL_GRADING.md (Windows: .venv-engine trong WSL).') from exc
