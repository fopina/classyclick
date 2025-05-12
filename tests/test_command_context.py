import os

import click
from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
    def test_argument(self):
        # example from https://click.palletsprojects.com/en/stable/complex/#the-root-command
        class Repo(object):
            def __init__(self, home=None, debug=False):
                self.home = os.path.abspath(home or '.')
                self.debug = debug

        @click.group()
        @click.option('--repo-home', envvar='REPO_HOME', default='.repo')
        @click.option('--debug/--no-debug', default=False, envvar='REPO_DEBUG')
        @click.pass_context
        def cli(ctx, repo_home, debug):
            ctx.obj = Repo(repo_home, debug)

        @classyclick.command(group=cli)
        class Clone:
            repo: Repo = classyclick.context_obj()
            src: str = classyclick.argument()
            dest: str = classyclick.argument(required=False)

            def __call__(self):
                click.echo(f'Clone from {self.src} to {self.dest} at {self.repo.home}')

        runner = CliRunner()
        result = runner.invoke(cli, args=['clone', '1'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, 'Clone from 1 to None at .*?/\.repo\n')
