from unittest import TestCase

import click
from click.testing import CliRunner


class Test(TestCase):
    """
    These tests are mostly to CONFIRM click behavior rather than to test it
    """

    def test_argument_name(self):
        """check that argument name is required and MUST match the variable"""

        @click.command()
        @click.argument('name')
        def my_command(name):
            click.echo(f'Hello, {name}')

        runner = CliRunner()

        result = runner.invoke(my_command, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Usage: my-command [OPTIONS] NAME', result.output)

        result = runner.invoke(my_command, args=[])
        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error: Missing argument 'NAME'", result.output)

        result = runner.invoke(my_command, args=['1'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello, 1\n')

        @click.command()
        @click.argument('name')
        def my_command_other(namex):
            click.echo(f'Hello, {namex}')

        runner = CliRunner()

        result = runner.invoke(my_command_other, args=['1'])
        # assert "name" positional must match variable name
        self.assertIn("got an unexpected keyword argument 'name'", str(result.exception))
        self.assertEqual(result.exit_code, 1)

        def _a():
            @click.command()
            @click.argument()
            def my_command_other(name):
                click.echo(f'Hello, {name}')

        # assert "name" positional is required
        self.assertRaisesRegex(TypeError, 'Argument is marked as exposed, but does not have a name', _a)

        @click.command()
        @click.argument('name', metavar='WTV')
        def my_command(name):
            click.echo(f'Hello, {name}')

        runner = CliRunner()

        result = runner.invoke(my_command, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertRegex(r'Usage: my.command \[OPTIONS\] WTV', result.output)

        result = runner.invoke(my_command, args=[])
        self.assertEqual(result.exit_code, 2)
        self.assertIn("Error: Missing argument 'WTV'", result.output)

        result = runner.invoke(my_command, args=['1'])
        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello, 1\n')
