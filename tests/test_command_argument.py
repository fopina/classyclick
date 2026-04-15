from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
    def test_argument(self):
        class Hello(classyclick.Command):
            name: str = classyclick.Argument()

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
        class Hello(classyclick.Command):
            name: str = classyclick.Argument(metavar='YOUR_NAME')

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
        class Sum(classyclick.Command):
            a: int = classyclick.Argument()
            # bad type hint but the explicit one supersedes, so test still passes
            b: str = classyclick.Argument(type=int)

            def __call__(self):
                print(self.a + self.b)

        runner = CliRunner()
        result = runner.invoke(Sum.click, ['1', '2'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '3\n')

    def test_type_override(self):
        class Sum(classyclick.Command):
            a: int = classyclick.Argument()
            # bad type hint but the explicit one supersedes, so test still passes
            b: str = classyclick.Argument(type=int)

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

        class DP(classyclick.Command):
            names: list[str] = classyclick.Argument(nargs=2)

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

    def test_type_list_nargs_variadic(self):
        """https://github.com/fopina/classyclick/issues/35"""

        # confirm Option multiple=True still works (as it did before the fix)
        class DP(classyclick.Command):
            p1: list[str] = classyclick.Option('-a', multiple=True)
            p2: list[str] = classyclick.Option('-b', nargs=2)

            def __call__(self):
                print(repr(self.p1), repr(self.p2))

        runner = CliRunner(catch_exceptions=False)

        result = runner.invoke(DP.click, ['-a', 'asd', '-a', 'qwe', '-b', 'foo', 'bar'])
        self.assertEqual(result.exception, None)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "('asd', 'qwe') ('foo', 'bar')\n")

        # confirm issue is fixed
        class DP(classyclick.Command):
            other_attachments: list[str] = classyclick.Argument(nargs=2)

            def __call__(self):
                print(repr(self.other_attachments))

        result = runner.invoke(DP.click, ['asd', 'qwe'])
        self.assertEqual(result.exception, None)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "('asd', 'qwe')\n")
