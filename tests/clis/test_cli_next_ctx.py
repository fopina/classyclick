from . import CliTestCase


class Test(CliTestCase):
    def test_cli_next_ctx(self):
        from ..cli_next_ctx import next_group

        result = self.invoker(next_group, ['next', '3'])

        self.assertEqual(result.output, '7\n')
