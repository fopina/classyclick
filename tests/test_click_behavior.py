import os

import click
from click.testing import CliRunner

from tests import BaseCase


class Test(BaseCase):
    """
    These tests are mostly to CONFIRM click behavior rather than to test it
    """

    def test_argument_name(self):
        """check that argument name is required and MUST match the variable"""

        @click.command()
        @click.argument('name')
        def hello(name):
            click.echo(f'Hello, {name}')

        runner = CliRunner()

        result = runner.invoke(hello, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, r'Usage: hello .*? NAME')

        result = runner.invoke(hello, args=[])
        self.assertEqual(result.exit_code, 2)
        self.assertRegex(result.output, r'Usage: hello .*? NAME')

        result = runner.invoke(hello, args=['1'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello, 1\n')

        @click.command()
        @click.argument('name')
        def hello_other(namex):
            click.echo(f'Hello, {namex}')

        runner = CliRunner()

        result = runner.invoke(hello_other, args=['1'])
        # assert "name" positional must match variable name
        self.assertIn("got an unexpected keyword argument 'name'", str(result.exception))
        self.assertEqual(result.exit_code, 1)

        def _a():
            @click.command()
            @click.argument()
            def hello_other(name):
                click.echo(f'Hello, {name}')

        # assert "name" positional is required
        # error changed in https://github.com/pallets/click/pull/2453
        if self.click_version >= (8, 1, 8):
            self.assertRaisesRegex(TypeError, 'Argument is marked as exposed, but does not have a name', _a)
        else:
            self.assertRaisesRegex(TypeError, 'Could not determine name for argument', _a)

        @click.command()
        @click.argument('name', metavar='WTV')
        def hello(name):
            click.echo(f'Hello, {name}')

        runner = CliRunner()

        result = runner.invoke(hello, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, r'Usage: hello .*? WTV')

        result = runner.invoke(hello, args=[])
        self.assertEqual(result.exit_code, 2)
        self.assertRegex(result.output, """Error: Missing argument ['"]WTV['"]""")

        result = runner.invoke(hello, args=['1'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello, 1\n')

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

        @cli.command()
        @click.argument('src')
        @click.argument('dest', required=False)
        @click.pass_obj
        def clone(repo, src, dest):
            click.echo(f'Clone from {src} to {dest} at {repo.home}')

        runner = CliRunner()

        result = runner.invoke(cli, args=['clone', '1'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, r'Clone from 1 to None at .*?/\.repo\n')

    def test_context_meta(self):
        if self.click_version < (8, 0):
            self.skipTest('pass_meta_key requires click 8.0')

        @click.group()
        @click.option('--repo-home', envvar='REPO_HOME', default='.repo')
        @click.pass_context
        def cli(ctx, repo_home):
            ctx.meta['repo'] = repo_home

        @cli.command()
        @click.argument('src')
        @click.argument('dest', required=False)
        @click.decorators.pass_meta_key('repo')
        def clone_key(repo, src, dest):
            click.echo(f'Clone from {src} to {dest} at {repo}')

        @cli.command()
        @click.argument('src')
        @click.argument('dest', required=False)
        @click.decorators.pass_meta_key('invkey')
        def clone_inv_key(repo, src, dest):
            click.echo(f'Clone from {src} to {dest} at {repo}')

        runner = CliRunner()

        result = runner.invoke(cli, args=['clone-key', '1'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Clone from 1 to None at .repo\n')

        result = runner.invoke(cli, args=['clone-inv-key', '1'])
        self.assertEqual(result.exception.args, KeyError('invkey').args)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, '')

    def test_naming(self):
        # "function to command" naming changed in 8.2.0 - https://github.com/pallets/click/issues/2322
        # as this opens up room for more "stripping" on top of just changing snake to kebab case, write test for it

        @click.command()
        def hello_there():
            pass

        self.assertEqual(hello_there.name, 'hello-there')

        @click.command()
        def hello_command():
            pass

        if self.click_version < (8, 2):
            self.assertEqual(hello_command.name, 'hello-command')
        else:
            self.assertEqual(hello_command.name, 'hello')

    def test_no_context_available(self):
        @click.command()
        @click.argument('src')
        @click.argument('dest', required=False)
        @click.pass_context
        def clone(o, src, dest):
            click.echo(f'Clone from {src} to {dest} at {o}')

        runner = CliRunner()

        result = runner.invoke(clone, args=['1'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(result.output, r'Clone from 1 to None at <click.core.Context.*?>\n')

    def test_no_context_obj_available(self):
        @click.command()
        @click.argument('src')
        @click.argument('dest', required=False)
        @click.pass_obj
        def clone(o, src, dest):
            click.echo(f'Clone from {src} to {dest} at {o}')

        runner = CliRunner()

        result = runner.invoke(clone, args=['1'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Clone from 1 to None at None\n')

    def test_no_context_meta_key_available(self):
        if self.click_version < (8, 0):
            self.skipTest('pass_meta_key requires click 8.0')

        @click.command()
        @click.argument('src')
        @click.argument('dest', required=False)
        @click.decorators.pass_meta_key('wtv')
        def clone(o, src, dest):
            click.echo(f'Clone from {src} to {dest} at {o}')

        runner = CliRunner()

        result = runner.invoke(clone, args=['1'])
        self.assertEqual(result.exception.__class__, KeyError)
        self.assertEqual(result.exception.args, ('wtv',))
        self.assertEqual(result.exit_code, 1)
