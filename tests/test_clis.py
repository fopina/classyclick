from unittest import TestCase

from click.testing import CliRunner

from .cli_one import Hello


class Test(TestCase):
    def test_hello(self):
        runner = CliRunner()
        result = runner.invoke(Hello, args=['--name', 'classyclick'])

        self.assertEqual(result.exit_code, 0)
        self.assertIn('Hello, classyclick!', result.output)

    def test_hello_class(self):
        kls = Hello.classy
        kls(name='classyclick')

    def test_hello_no_types(self):
        def _a():
            from .cli_two import Hello

            # no-op until "ruff format" gets pragma support (like # fmt: off)
            Hello

        self.assertRaisesRegex(TypeError, "tests.cli_two.Hello is missing type for option/argument 'name'", _a)

    def test_bye(self):
        from .cli_three import Bye

        runner = CliRunner()
        result = runner.invoke(Bye, args=['--name', 'classyclick'])

        self.assertEqual(result.exit_code, 0)
        self.assertIn('Bye, classyclick!', result.output)

    def test_next(self):
        from .cli_four import Next

        runner = CliRunner()
        result = runner.invoke(Next, args=['3'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '4\n')
