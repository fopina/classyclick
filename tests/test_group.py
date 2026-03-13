import click
from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_group(self):
        @click.group
        def cli(): ...

        class Hello(classyclick.Command):
            """test command"""

            __config__ = classyclick.Command.Config(group=cli)

            name: str = classyclick.Argument()
            age: int = classyclick.Option(default=10)

            def __call__(self): ...

        result = self.runner.invoke(cli, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: cli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  hello  test command
""",
        )
        result = self.runner.invoke(cli, args=['hello', '--help'])
        self.assertEqual(result.exit_code, 0)
        # match just the prefix
        self.assertEqual(
            result.output[:48],
            """\
Usage: cli hello [OPTIONS] NAME

  test command
""",
        )

    def test_group_default_name(self):
        class Cli(classyclick.Group): ...

        self.assertEqual(Cli.click.name, 'cli')

    def test_group_fields_and_subcommands(self):
        class Cli(classyclick.Group):
            """test group"""

            count: int = classyclick.Option(default=1, help='Number of times.')

            def __call__(self): ...

        class Hello(classyclick.Command):
            """test command"""

            __config__ = classyclick.Command.Config(group=Cli.click)

            name: str = classyclick.Argument()

            def __call__(self): ...

        result = self.runner.invoke(Cli.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Usage: cli [OPTIONS] COMMAND [ARGS]...', result.output)
        self.assertIn('  --count INTEGER', result.output)
        self.assertIn('  hello  test command', result.output)
