from unittest import TestCase

from click.testing import CliRunner

import classyclick


class Test(TestCase):
    @property
    def click_version(self):
        from click import __version__

        return tuple(map(int, __version__.split('.')))

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

        if self.click_version >= (8, 0):
            self.assertIn("Error: Missing argument 'NAME'", result.output)
        elif self.click_version >= (7, 0):
            self.assertIn('Error: Missing argument "NAME"', result.output)
        else:
            self.assertIn('Error: Missing argument "name"', result.output)

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

    def test_type_inference_option(self):
        @classyclick.command()
        class Sum:
            a: int = classyclick.option()
            b: int = classyclick.option()

            def __call__(self):
                print(self.a + self.b)

        runner = CliRunner()
        result = runner.invoke(Sum, ['--a', '1', '--b', '2'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '3\n')

    def test_type_inference_argument(self):
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

    def test_field_not_argument(self):
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
