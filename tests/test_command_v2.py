import click
from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_command_default_name(self):
        class Hello(classyclick.Command): ...

        self.assertEqual(Hello.click.name, 'hello')

        class HelloThere(classyclick.Command): ...

        self.assertEqual(HelloThere.click.name, 'hello-there')

        class HelloThereCommand(classyclick.Command): ...

        if self.click_version < (8, 2):
            self.assertEqual(HelloThereCommand.click.name, 'hello-there-command')
        else:
            self.assertEqual(HelloThereCommand.click.name, 'hello-there')

    def test_init_defaults(self):
        class Hello(classyclick.Command):
            name: str = classyclick.Argument()
            age: int = classyclick.Option(default=10)

            def __call__(self):
                print(f'Hello {self.name}, gratz on being {self.age}')

        result = self.runner.invoke(Hello.click, ['John'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello John, gratz on being 10\n')

        with self.assertRaisesRegex(TypeError, "missing 1 required positional argument: 'name'"):
            Hello()
        obj = Hello(name='John')
        self.assertEqual(obj.name, 'John')
        self.assertEqual(obj.age, 10)

    def test_defaults_and_required(self):
        """https://github.com/fopina/classyclick/issues/30"""

        class BaseHello(classyclick.Command):
            age: int = classyclick.Option(default=10)
            # str Option without explicit default, means default=None - make sure dataclass also takes it as such
            name: str = classyclick.Option()

            def __call__(self):
                print(f'Hello {self.name}, gratz on being {self.age}')

        result = self.runner.invoke(BaseHello.click)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello None, gratz on being 10\n')

        class Hello(BaseHello):
            age: int = classyclick.Option(default=10)
            # str Option without explicit default, means default=None - make sure dataclass also takes it as such
            name: str = classyclick.Argument(required=False)

            def __call__(self):
                print(f'Hello {self.name}, gratz on being {self.age}')

        result = self.runner.invoke(Hello.click)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello None, gratz on being 10\n')

        class Hello(BaseHello):
            age: int = classyclick.Option(default=10)
            # str Option without explicit default, means default=None - make sure dataclass also takes it as such
            name: str = classyclick.Argument(default='John')

            def __call__(self):
                print(f'Hello {self.name}, gratz on being {self.age}')

        result = self.runner.invoke(Hello.click)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello John, gratz on being 10\n')

    def test_defaults_and_required_bad(self):
        """https://github.com/fopina/classyclick/issues/30"""

        with self.assertRaisesRegex(TypeError, "non-default argument 'name' follows default argument"):

            class Hello(classyclick.Command):
                age: int = classyclick.Option(default=10)
                name: str = classyclick.Option(required=True)

                def __call__(self): ...

        with self.assertRaisesRegex(TypeError, "non-default argument 'name' follows default argument"):

            class Hello(classyclick.Command):
                age: int = classyclick.Option(default=10)
                name: str = classyclick.Option(required=True)

                def __call__(self): ...

        with self.assertRaisesRegex(TypeError, "non-default argument 'name' follows default argument"):

            class Hello(classyclick.Command):
                age: int = classyclick.Option(default=10)
                name: str = classyclick.Argument()

                def __call__(self): ...

    def test_name_and_help(self):
        class Hello(classyclick.Command):
            """test command"""

            name: str = classyclick.Argument()
            age: int = classyclick.Option(default=10)

            def __call__(self): ...

        result = self.runner.invoke(Hello.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: hello [OPTIONS] NAME

  test command

Options:
  --age INTEGER
  --help         Show this message and exit.
""",
        )

        class Hello(classyclick.Command):
            """test command"""

            __config__ = classyclick.Command.Config(help='override pydocs', name='hello-there')

            name: str = classyclick.Argument()
            age: int = classyclick.Option(default=10)

            def __call__(self): ...

        result = self.runner.invoke(Hello.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: hello-there [OPTIONS] NAME

  override pydocs

Options:
  --age INTEGER
  --help         Show this message and exit.
""",
        )

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

    def test_config_supports_click_kwargs(self):
        class Hello(classyclick.Command):
            """test command"""

            __config__ = classyclick.Command.Config(name='hello-there', help='override')

            name: str = classyclick.Argument()
            age: int = classyclick.Option(default=10)

            def __call__(self): ...

        result = self.runner.invoke(Hello.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: hello-there [OPTIONS] NAME

  override

Options:
  --age INTEGER
  --help         Show this message and exit.
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
