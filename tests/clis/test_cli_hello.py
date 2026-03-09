from . import CliTestCase, load_cli_script


class Test(CliTestCase):
    def test_cli_hello(self):
        module = load_cli_script('cli_hello.py')

        result = self.invoker(module.Hello.click, ['--name', 'classyclick', '--count', '2'])

        self.assertEqual(result.output, 'Hello, kcilcyssalc!\nHello, kcilcyssalc!\n')
