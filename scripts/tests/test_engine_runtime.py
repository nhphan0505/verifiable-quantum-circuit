"""Runtime selection rejects missing WSL and preserves argument boundaries."""
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

path = Path(__file__).resolve().parents[2] / 'src/common/engine_runtime.py'
spec = importlib.util.spec_from_file_location('engine_runtime_test', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Runtime(unittest.TestCase):
    def test_missing_wsl_is_actionable(self):
        with patch.object(m.sys, 'platform', 'win32'), patch.object(m.subprocess, 'run', side_effect=FileNotFoundError):
            with self.assertRaisesRegex(RuntimeError, 'wsl --install -d Ubuntu'):
                m.runtime(Path.cwd())

    def test_native_uses_kernel(self):
        with patch.object(m.sys, 'platform', 'linux'):
            prefix, root = m.runtime(Path.cwd())
        self.assertEqual(prefix, [m.sys.executable])
        self.assertEqual(root, str(Path.cwd().resolve()))

    def test_missing_engine_is_actionable(self):
        with patch.object(m.subprocess, 'check_output', side_effect=subprocess.CalledProcessError(1, 'python')):
            with self.assertRaisesRegex(RuntimeError, '0.6.0'):
                m.preflight(['python'])

    def test_wsl_space_path_is_one_argument(self):
        with patch.object(m.sys, 'platform', 'win32'), patch.object(m.subprocess, 'run') as run, patch.object(m.subprocess, 'check_output', return_value='/mnt/d/My Project\n'):
            run.return_value.returncode = 0
            prefix, root = m.runtime(Path.cwd())
        self.assertEqual(prefix, ['wsl.exe', '--exec', '/mnt/d/My Project/.venv-engine/bin/python'])
