from . import CliTestCase


class Test(CliTestCase):
    def test_cli_bye(self):
        from ..cli_bye import PlainBye

        result = self.invoker(PlainBye.click, ['--name', 'classyclick'])
        self.assertEqual(result.output, 'Bye, classyclick!\n')
