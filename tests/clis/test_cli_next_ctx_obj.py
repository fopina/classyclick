from . import CliTestCase


class Test(CliTestCase):
    def test_cli_next_ctx_obj(self):
        from ..cli_next_ctx_obj import NextGroup

        result = self.invoker(NextGroup.click, ['next', '3'])

        self.assertEqual(result.output, '7\n')
