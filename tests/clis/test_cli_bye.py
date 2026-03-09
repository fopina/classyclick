from . import CliTestCase, load_cli_script


class Test(CliTestCase):
    def test_cli_bye(self):
        module = load_cli_script('cli_bye.py')

        result = self.invoker(module.Bye.click, ['--name', 'classyclick'])

        self.assertEqual(result.output, 'Bye, kcilcyssalc!\n')
