from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
    @property
    def click_version(self):
        from click import __version__

        return tuple(map(int, __version__.split('.')))

    def test_option(self):
        @classyclick.command()
        class Hello:
            name: str = classyclick.option(help='Name')

            def __call__(self):
                print(f'Hello, {self.name}')

        runner = CliRunner()
        result = runner.invoke(Hello.click, ['--name', 'Peter'])
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
        result = runner.invoke(Sum.click, ['--a', '1', '--b', '2'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '3\n')

    def test_cannot_choose_name(self):
        def _a():
            @classyclick.command()
            class Sum:
                a: int = classyclick.option('arc')

                def __call__(self):
                    print(self.a + self.b)

        self.assertRaisesRegex(TypeError, 'sum option a: do not specify a name, it is already added', _a)

    def test_no_default_parameter(self):
        @classyclick.command()
        class DP:
            name: str = classyclick.option()
            extra: str = classyclick.option('--xtra', default_parameter=False)

            def __call__(self):
                print(f'Hello, {self.name}{self.extra}')

        runner = CliRunner()

        result = runner.invoke(DP.click, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, r'\n  --name TEXT')
        self.assertRegex(result.output, r'\n  --xtra TEXT')

        result = runner.invoke(DP.click, ['--name', 'world', '--xtra', '!'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello, world!\n')

    def test_type_bool(self):
        """test implicit is_flag=True for type bool"""

        @classyclick.command()
        class DP:
            greet: bool = classyclick.option()
            other: bool = classyclick.option(is_flag=False)

            def __call__(self):
                if self.greet:
                    print('Hello')

        runner = CliRunner()

        result = runner.invoke(DP.click, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, r'\n  --greet\n')
        # when is_flag=False, even with type=bool, help reflects it
        self.assertRegex(result.output, r'\n  --other BOOLEAN\n')

        result = runner.invoke(DP.click, [])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '')

        result = runner.invoke(DP.click, ['--greet'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello\n')

    def test_type_list_multiple(self):
        """test click type is properly set to X when using field type list[X]"""

        @classyclick.command()
        class DP:
            names: list[str] = classyclick.option('--name', default_parameter=False, metavar='NAME', multiple=True)

            def __call__(self):
                print(f'Hello, {" and ".join(self.names)}')

        runner = CliRunner()

        result = runner.invoke(DP.click, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, '\n  --name NAME\n')

        result = runner.invoke(DP.click, ['--name', 'john', '--name', 'paul'])
        self.assertEqual(result.exception, None)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello, john and paul\n')

    def test_type_list_nargs(self):
        """test click type is properly set to X when using field type list[X]"""

        @classyclick.command()
        class DP:
            names: list[str] = classyclick.option('--name', metavar='NAME', default_parameter=False, nargs=2)

            def __call__(self):
                print(f'Hello, {" and ".join(self.names)}')

        runner = CliRunner()

        result = runner.invoke(DP.click, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, '\n  --name NAME\n')

        result = runner.invoke(DP.click, ['--name', 'john', 'paul'])
        self.assertEqual(
            (
                result.exception,
                result.exit_code,
                result.output,
            ),
            (None, 0, 'Hello, john and paul\n'),
        )
