from . import CliTestCase


class Test(CliTestCase):
    def test_cli_next_ctx_obj(self):
        from ..cli_next_ctx_obj import next_group

        result = self.invoker(next_group, ['next', '3'])

        self.assertEqual(result.output, '7\n')
