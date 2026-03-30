from . import CliTestCase


class Test(CliTestCase):
    def test_cli_hello(self):
        from ..cli_hello import Hello

        result = self.invoker(Hello.click, ['--name', 'classyclick', '-c', '2'])

        self.assertEqual(result.output, 'Hello, classyclick!\nHello, classyclick!\n')
