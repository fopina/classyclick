from unittest import TestCase

from click.testing import CliRunner

from .cli_one import Hello


class Test(TestCase):
    def test_hello(self):
        runner = CliRunner()
        result = runner.invoke(Hello, args=['--name', 'classyclick'])

        self.assertEqual(result.exit_code, 0)
        self.assertIn('Hello, Alice!', result.output)
