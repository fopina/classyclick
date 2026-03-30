from . import CliTestCase


class Test(CliTestCase):
    def test_cli_bye(self):
        from ..cli_bye import Bye

        result = self.invoker(Bye.click, ['--name', 'classyclick'])
        self.assertEqual(result.output, 'Bye, classyclick!\n')
