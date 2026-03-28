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

            def __call__(self):
                print(f'Hello {self.name}')

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
        result = self.runner.invoke(cli, args=['hello', 'John'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello John\n')

    def test_group_default_name(self):
        class Cli(classyclick.Group): ...

        self.assertEqual(Cli.click.name, 'cli')

    def test_group_help_without_docstring_is_empty(self):
        class Cli(classyclick.Group): ...

        result = self.runner.invoke(Cli.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: cli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.
""",
        )

    def test_group_inherited_docstring_used_for_help(self):
        class BaseCli(classyclick.Group):
            """shared group help"""

        class Cli(BaseCli):
            pass

        result = self.runner.invoke(Cli.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: cli [OPTIONS] COMMAND [ARGS]...

  shared group help

Options:
  --help  Show this message and exit.
""",
        )

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

    def test_group_command_mixin(self):
        class CLI(classyclick.Group):
            """Shared group help"""

        class Hello(CLI.Command):
            """Say hello"""

            name: str = classyclick.Argument()

            def __call__(self):
                print(f'Hello {self.name}')

        result = self.runner.invoke(CLI.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: cli [OPTIONS] COMMAND [ARGS]...

  Shared group help

Options:
  --help  Show this message and exit.

Commands:
  hello  Say hello
""",
        )
        result = self.runner.invoke(CLI.click, args=['hello', 'John'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello John\n')

    def test_group_command_mixin_still_available(self):
        class CLI(classyclick.Group):
            """Shared group help"""

        class Hello(CLI.CommandMixin, classyclick.Command):
            """Say hello"""

            name: str = classyclick.Argument()

            def __call__(self):
                print(f'Hello {self.name}')

        result = self.runner.invoke(CLI.click, args=['hello', 'John'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello John\n')

    def test_nested_group_uses_base_config_and_command_subclass(self):
        class Cli(classyclick.Group):
            """test group"""

        class SubGroup(Cli.SubGroup):
            """subgroup"""

        class Status(SubGroup.Command):
            """show status"""

            item: str = classyclick.Argument()

            def __call__(self):
                print(f'{self.item} is here')

        root_result = self.runner.invoke(Cli.click, args=['--help'])
        self.assertEqual(root_result.exit_code, 0)
        if self.click_version < (8, 2):
            sub_cmd = 'sub-group'
        else:
            sub_cmd = 'sub'
        self.assertEqual(
            root_result.output,
            f"""\
Usage: cli [OPTIONS] COMMAND [ARGS]...

  test group

Options:
  --help  Show this message and exit.

Commands:
  {sub_cmd}  subgroup
""",
        )

        subgroup_result = self.runner.invoke(Cli.click, args=[sub_cmd, '--help'])
        self.assertEqual(subgroup_result.exit_code, 0)
        self.assertEqual(
            subgroup_result.output,
            f"""\
Usage: cli {sub_cmd} [OPTIONS] COMMAND [ARGS]...

  subgroup

Options:
  --help  Show this message and exit.

Commands:
  status  show status
""",
        )
        subgroup_result = self.runner.invoke(Cli.click, args=[sub_cmd, 'status', 'fork'])
        self.assertEqual(subgroup_result.exit_code, 0)
        self.assertEqual(subgroup_result.output, 'fork is here\n')
