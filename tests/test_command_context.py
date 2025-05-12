import os
from typing import Any

import click
from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
    def test_context(self):
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

        @classyclick.command(group=cli)
        class Clone2:
            ctx: Any = classyclick.context()
            src: str = classyclick.argument()
            dest: str = classyclick.argument(required=False)

            def __call__(self):
                click.echo(f'Clone from {self.src} to {self.dest} at {self.ctx.obj.home}')

        runner = CliRunner()

        result = runner.invoke(cli, args=['clone', '1', '2'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, r'Clone from 1 to 2 at .*?/\.repo\n')

        result = runner.invoke(cli, args=['clone2', '1', '2'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, r'Clone from 1 to 2 at .*?/\.repo\n')

    def test_context_meta(self):
        if self.click_version < (8, 0):
            self.skipTest('pass_meta_key requires click 8.0')

        @click.group()
        @click.option('--repo-home', envvar='REPO_HOME', default='.repo')
        @click.option('--debug/--no-debug', default=False, envvar='REPO_DEBUG')
        @click.pass_context
        def cli(ctx, repo_home, debug):
            ctx.meta['repo'] = repo_home
            ctx.meta['debug'] = debug

        @classyclick.command(group=cli)
        class Clone:
            repo: str = classyclick.context_meta('repo')
            debug: bool = classyclick.context_meta('debug')
            src: str = classyclick.argument()
            dest: str = classyclick.argument(required=False)

            def __call__(self):
                click.echo(f'Clone from {self.src} to {self.dest} at {self.repo}')

        runner = CliRunner()

        result = runner.invoke(cli, args=['clone', '1', '2'])
        self.assertEqual(result.output, 'Clone from 1 to 2 at .repo\n')
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
