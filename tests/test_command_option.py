from unittest import TestCase

from click.testing import CliRunner

import classyclick


class Test(TestCase):
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
        result = runner.invoke(Hello, ['--name', 'Peter'])
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

    def test_cannot_choose_name(self):
        def _a():
            @classyclick.command()
            class Sum:
                a: int = classyclick.option('arc')

                def __call__(self):
                    print(self.a + self.b)

        self.assertRaisesRegex(TypeError, '.Sum option a: do not specify a name, it is already added', _a)
