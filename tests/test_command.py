from unittest import TestCase

from click.testing import CliRunner

import classyclick


class Test(TestCase):
    def test_error(self):
        def not_a_class():
            @classyclick.command()
            def hello():
                pass

        self.assertRaisesRegex(ValueError, 'hello is not a class', not_a_class)

    def test_option(self):
        @classyclick.command()
        class Hello:
            name: str = classyclick.option(help='Name')

            def __call__(self):
                print(f'Hello, {self.name}')

        runner = CliRunner()
        result = runner.invoke(Hello, ['--name', 'Peter'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello, Peter\n')

    def test_argument(self):
        @classyclick.command()
        class Hello:
            name: str = classyclick.argument()

            def __call__(self):
                print(f'Hello, {self.name}')

        runner = CliRunner()
        result = runner.invoke(Hello)
        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error: Missing argument 'NAME'", result.output)

        result = runner.invoke(Hello, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: hello [OPTIONS] NAME

Options:
  --help  Show this message and exit.
""",
        )

        result = runner.invoke(Hello, ['Peter'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello, Peter\n')
