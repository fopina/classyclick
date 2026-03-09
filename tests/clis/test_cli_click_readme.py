from . import CliTestCase, load_cli_script


class Test(CliTestCase):
    def test_cli_click_readme(self):
        module = load_cli_script('cli_click_readme.py')

        result = self.invoker(module.hello, ['--name', 'classyclick', '--count', '2'])

        self.assertEqual(result.output, 'Hello, kcilcyssalc!\nHello, kcilcyssalc!\n')
