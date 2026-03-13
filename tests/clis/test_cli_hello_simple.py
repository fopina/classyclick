from . import CliTestCase


class Test(CliTestCase):
    def test_cli_hello_simple(self):
        from ..cli_hello_simple import Hello

        result = self.invoker(Hello.click, ['--name', 'classyclick', '--count', '2'])

        self.assertEqual(result.output, 'Hello, classyclick!\nHello, classyclick!\n')
