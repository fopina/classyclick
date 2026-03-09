from types import SimpleNamespace

import click

from . import CliTestCase, load_cli_script


class Test(CliTestCase):
    def test_cli_next_ctx(self):
        module = load_cli_script('cli_next_ctx.py')

        @click.group()
        @click.pass_context
        def cli(ctx):
            ctx.obj = SimpleNamespace(step_number=4)

        cli.add_command(module.Next.click)

        result = self.invoker(cli, ['next', '3'])

        self.assertEqual(result.output, '7\n')
