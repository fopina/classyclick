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

        class CLI(classyclick.Group):
            repo_home: str = classyclick.Option(envvar='REPO_HOME', default='.repo')
            debug: bool = classyclick.Option('--debug/--no-debug', default_parameter=False, envvar='REPO_DEBUG')
            ctx: click.Context = classyclick.Context()

            def __call__(self):
                self.ctx.obj = Repo(self.repo_home, self.debug)

        class Clone(CLI.Command):
            src: str = classyclick.Argument()
            dest: str = classyclick.Argument(required=False)
            repo: Repo = classyclick.ContextObj()

            def __call__(self):
                click.echo(f'Clone from {self.src} to {self.dest} at {self.repo.home}')

        class Clone2(CLI.Command):
            src: str = classyclick.Argument()
            ctx: Any = classyclick.Context()
            dest: str = classyclick.Argument(required=False)

            def __call__(self):
                click.echo(f'Clone from {self.src} to {self.dest} at {self.ctx.obj.home}')

        runner = CliRunner()

        result = runner.invoke(CLI.click, args=['clone', '1', '2'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, r'Clone from 1 to 2 at .*?/\.repo\n')

        result = runner.invoke(CLI.click, args=['clone2', '1', '2'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, r'Clone from 1 to 2 at .*?/\.repo\n')

    def test_context_meta(self):
        if self.click_version < (8, 0):
            self.skipTest('pass_meta_key requires click 8.0')

        class CLI(classyclick.Group):
            repo_home: str = classyclick.Option(envvar='REPO_HOME', default='.repo')
            debug: bool = classyclick.Option('--debug/--no-debug', default_parameter=False, envvar='REPO_DEBUG')
            ctx: click.Context = classyclick.Context()

            def __call__(self):
                self.ctx.meta['repo'] = self.repo_home
                self.ctx.meta['debug'] = self.debug

        class Clone(CLI.Command):
            repo: str = classyclick.ContextMeta('repo')
            debug: bool = classyclick.ContextMeta('debug')
            src: str = classyclick.Argument()
            dest: str = classyclick.Argument(required=False)

            def __call__(self):
                click.echo(f'Clone from {self.src} to {self.dest} at {self.repo}')

        runner = CliRunner()

        result = runner.invoke(CLI.click, args=['clone', '1', '2'])
        self.assertEqual(result.output, 'Clone from 1 to 2 at .repo\n')
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
