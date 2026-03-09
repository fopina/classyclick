import click

from tests import BaseCase

from . import CliTestCase, load_cli_script


class Test(CliTestCase, BaseCase):
    def test_cli_next_ctx_meta(self):
        if self.click_version < (8, 0):
            self.skipTest('pass_meta_key requires click 8.0')

        module = load_cli_script('cli_next_ctx_meta.py')

        @click.group()
        @click.pass_context
        def cli(ctx):
            ctx.meta['step_number'] = 5

        cli.add_command(module.Next.click)

        result = self.invoker(cli, ['next', '3'])

        self.assertEqual(result.output, '8\n')
