from . import CliTestCase


class Test(CliTestCase):
    def test_cli_click_readme(self):
        from ..cli_click_readme import hello

        result = self.invoker(hello, ['--name', 'classyclick', '--count', '2'])

        self.assertEqual(result.output, 'Hello, kcilcyssalc!\nHello, kcilcyssalc!\n')
