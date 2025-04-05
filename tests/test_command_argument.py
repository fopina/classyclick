from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
    def test_argument(self):
        @classyclick.command()
        class Hello:
            name: str = classyclick.argument()

            def __call__(self):
                print(f'Hello, {self.name}')

        runner = CliRunner()
        result = runner.invoke(Hello)
        self.assertEqual(result.exit_code, 2)

        if self.click_version >= (8, 0):
            self.assertIn("Error: Missing argument 'NAME'", result.output)
        else:
            self.assertIn('Error: Missing argument "NAME"', result.output)

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

    def test_metavar(self):
        @classyclick.command()
        class Hello:
            name: str = classyclick.argument(metavar='YOUR_NAME')

            def __call__(self):
                print(f'Hello, {self.name}')

        runner = CliRunner()
        result = runner.invoke(Hello, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: hello [OPTIONS] YOUR_NAME

Options:
  --help  Show this message and exit.
""",
        )

        result = runner.invoke(Hello, ['Peter'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello, Peter\n')

    def test_type_inference(self):
        @classyclick.command()
        class Sum:
            a: int = classyclick.argument()
            # bad type hint but the explicit one supersedes, so test still passes
            b: str = classyclick.argument(type=int)

            def __call__(self):
                print(self.a + self.b)

        runner = CliRunner()
        result = runner.invoke(Sum, ['1', '2'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '3\n')

    def test_type_override(self):
        @classyclick.command()
        class Sum:
            a: int = classyclick.argument()
            # bad type hint but the explicit one supersedes, so test still passes
            b: str = classyclick.argument(type=int)

            def __call__(self):
                print(self.a + self.b)

        runner = CliRunner()
        result = runner.invoke(Sum, ['1', '2'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '3\n')
