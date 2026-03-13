from types import SimpleNamespace

import click

from . import CliTestCase


class Test(CliTestCase):
    def test_cli_next_ctx(self):
        from ..cli_next_ctx import Next

        @click.group()
        @click.pass_context
        def cli(ctx):
            ctx.obj = SimpleNamespace(step_number=4)

        cli.add_command(Next.click)

        result = self.invoker(cli, ['next', '3'])

        self.assertEqual(result.output, '7\n')
