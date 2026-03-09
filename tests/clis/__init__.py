from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest import TestCase

from click.testing import CliRunner

TESTS_DIR = Path(__file__).resolve().parents[1]


def load_cli_script(script: str) -> ModuleType:
    path = TESTS_DIR / script
    module_name = f'tests.clis._loaded_{path.stem}'
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Unable to load CLI script {path}')

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    original_sys_path = list(sys.path)
    sys.path.insert(0, str(TESTS_DIR))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = original_sys_path

    return module


class CliTestCase(TestCase):
    def invoker(self, command, args: list[str]):
        runner = CliRunner()
        result = runner.invoke(command, args=args)
        self.assertIsNone(result.exception, result.output)
        self.assertEqual(result.exit_code, 0, result.output)
        return result
