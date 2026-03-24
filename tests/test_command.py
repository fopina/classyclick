import click
from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_error(self):
        def not_a_class():
            @classyclick.command()
            def hello():
                pass

        self.assertRaisesRegex(ValueError, 'hello is not a class', not_a_class)

    def test_command_default_name(self):
        @classyclick.command()
        class Hello: ...

        self.assertEqual(Hello.click.name, 'hello')

        @classyclick.command()
        class HelloThere: ...

        self.assertEqual(HelloThere.click.name, 'hello-there')

        @classyclick.command()
        class HelloThereCommand: ...

        if self.click_version < (8, 2):
            self.assertEqual(HelloThereCommand.click.name, 'hello-there-command')
        else:
            self.assertEqual(HelloThereCommand.click.name, 'hello-there')

    def test_init_defaults(self):
        @classyclick.command()
        class Hello:
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

        @classyclick.command()
        class BaseHello:
            age: int = classyclick.Option(default=10)
            # str Option without explicit default, means default=None - make sure dataclass also takes it as such
            name: str = classyclick.Option()

            def __call__(self):
                print(f'Hello {self.name}, gratz on being {self.age}')

        result = self.runner.invoke(BaseHello.click)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello None, gratz on being 10\n')

        @classyclick.command()
        class Hello(BaseHello):
            age: int = classyclick.Option(default=10)
            # str Option without explicit default, means default=None - make sure dataclass also takes it as such
            name: str = classyclick.Argument(required=False)

        result = self.runner.invoke(Hello.click)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello None, gratz on being 10\n')

        @classyclick.command()
        class Hello(BaseHello):
            age: int = classyclick.Option(default=10)
            # str Option without explicit default, means default=None - make sure dataclass also takes it as such
            name: str = classyclick.Argument(default='John')

        result = self.runner.invoke(Hello.click)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello John, gratz on being 10\n')

    def test_defaults_and_required_bad(self):
        """https://github.com/fopina/classyclick/issues/30"""

        with self.assertRaisesRegex(TypeError, "non-default argument 'name' follows default argument"):

            @classyclick.command()
            class Hello:
                age: int = classyclick.Option(default=10)
                name: str = classyclick.Option(required=True)

                def __call__(self): ...

        with self.assertRaisesRegex(TypeError, "non-default argument 'name' follows default argument"):

            @classyclick.command()
            class Hello:
                age: int = classyclick.Option(default=10)
                name: str = classyclick.Option(required=True)

                def __call__(self): ...

        with self.assertRaisesRegex(TypeError, "non-default argument 'name' follows default argument"):

            @classyclick.command()
            class Hello:
                age: int = classyclick.Option(default=10)
                name: str = classyclick.Argument()

                def __call__(self): ...

    def test_name_and_help(self):
        @classyclick.command()
        class Hello:
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

        @classyclick.command(help='override pydocs', name='hello-there')
        class Hello:
            """test command"""

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

        @classyclick.command(group=cli)
        class Hello:
            """test command"""

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

    def test_option_help_from_attribute_docstring(self):
        @classyclick.command()
        class Hello:
            name: str = classyclick.Option()
            """The person to greet."""

            def __call__(self): ...

        result = self.runner.invoke(Hello.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('  --name TEXT  The person to greet.', result.output)

    def test_explicit_option_help_overrides_attribute_docstring(self):
        @classyclick.command()
        class Hello:
            name: str = classyclick.Option(help='Explicit help')
            """The person to greet."""

            def __call__(self): ...

        result = self.runner.invoke(Hello.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('  --name TEXT  Explicit help', result.output)
        self.assertNotIn('The person to greet.', result.output)
