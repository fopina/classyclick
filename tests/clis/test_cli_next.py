from . import CliTestCase


class Test(CliTestCase):
    def test_cli_next(self):
        from ..cli_next import Next

        result = self.invoker(Next.click, ['3'])

        self.assertEqual(result.output, '4\n')
