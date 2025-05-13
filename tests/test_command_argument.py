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
        result = runner.invoke(Hello.click)
        self.assertEqual(result.exit_code, 2)

        # click changed from " ' in 8.0.0
        self.assertRegex(result.output, """Error: Missing argument ['"]NAME['"]""")

        result = runner.invoke(Hello.click, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: hello [OPTIONS] NAME

Options:
  --help  Show this message and exit.
""",
        )

        result = runner.invoke(Hello.click, ['Peter'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello, Peter\n')

    def test_metavar(self):
        @classyclick.command()
        class Hello:
            name: str = classyclick.argument(metavar='YOUR_NAME')

            def __call__(self):
                print(f'Hello, {self.name}')

        runner = CliRunner()
        result = runner.invoke(Hello.click, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: hello [OPTIONS] YOUR_NAME

Options:
  --help  Show this message and exit.
""",
        )

        result = runner.invoke(Hello.click, ['Peter'])
        self.assertEqual(result.exception, None)
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
        result = runner.invoke(Sum.click, ['1', '2'])
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
        result = runner.invoke(Sum.click, ['1', '2'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '3\n')

    def test_type_list_nargs(self):
        """
        test click type is properly set to X when using field type list[X]
         - only nargs, multiple=True is not supported in click.argument
        """

        @classyclick.command()
        class DP:
            names: list[str] = classyclick.argument(nargs=2)

            def __call__(self):
                print(f'Hello, {" and ".join(self.names)}')

        runner = CliRunner()

        result = runner.invoke(DP.click, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, r'\[OPTIONS\] NAMES...\n')

        result = runner.invoke(DP.click, ['john', 'paul'])
        self.assertEqual(
            (
                result.exception,
                result.exit_code,
                result.output,
            ),
            (None, 0, 'Hello, john and paul\n'),
        )
