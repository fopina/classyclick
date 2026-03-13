from __future__ import annotations

import sys
from pathlib import Path
from unittest import TestCase

from click.testing import CliRunner

# add tests to sys.path because some cli_* import others (without relative imports)
sys.path.append(str(Path(__file__).parent.parent))

TESTS_DIR = Path(__file__).resolve().parents[1]


class CliTestCase(TestCase):
    def invoker(self, command, args: list[str]):
        runner = CliRunner()
        result = runner.invoke(command, args=args)
        self.assertIsNone(result.exception, result.output)
        self.assertEqual(result.exit_code, 0, result.output)
        return result
