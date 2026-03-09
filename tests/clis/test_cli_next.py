from . import CliTestCase, load_cli_script


class Test(CliTestCase):
    def test_cli_next(self):
        module = load_cli_script('cli_next.py')

        result = self.invoker(module.Next.click, ['3'])

        self.assertEqual(result.output, '4\n')
