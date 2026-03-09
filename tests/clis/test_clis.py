import subprocess
import sys
from pathlib import Path
from unittest import TestCase


class Test(TestCase):
    def _run_cli(self, script: str, args: list[str]):
        path = Path(__file__).resolve().parents[1] / script
        return subprocess.run(
            [sys.executable, str(path), *args],
            check=False,
            cwd=str(path.parent.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    def test_hello(self):
        result = self._run_cli('cli_hello.py', ['--name', 'classyclick'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Hello, kcilcyssalc!', result.stdout)

    def test_bye(self):
        result = self._run_cli('cli_bye.py', ['--name', 'classyclick'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Bye, kcilcyssalc!', result.stdout)

    def test_next(self):
        result = self._run_cli('cli_next.py', ['3'])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '4\n')
