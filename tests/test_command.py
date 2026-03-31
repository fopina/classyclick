import click
from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_command_default_name(self):
        class Hello(classyclick.Command):
            def __call__(self): ...

        self.assertEqual(Hello.click.name, 'hello')

        class HelloThere(classyclick.Command):
            def __call__(self): ...

        self.assertEqual(HelloThere.click.name, 'hello-there')

        class HelloThereCommand(classyclick.Command):
            def __call__(self): ...

        if self.click_version < (8, 2):
            self.assertEqual(HelloThereCommand.click.name, 'hello-there-command')
        else:
            self.assertEqual(HelloThereCommand.click.name, 'hello-there')

    def test_missing_call_raises_early(self):
        with self.assertRaisesRegex(NotImplementedError, 'has not implemented __call__()'):

            class Hello(classyclick.Command):
                pass

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

    def test_prompted_option_is_required_for_object_init_without_explicit_default(self):
        class Hello(classyclick.Command):
            name: str = classyclick.Option(prompt='Your name')
            age: int = classyclick.Option(default=10)

            def __call__(self): ...

        with self.assertRaisesRegex(TypeError, "missing 1 required positional argument: 'name'"):
            Hello()

        obj = Hello('John', 20)
        self.assertEqual(obj.name, 'John')
        self.assertEqual(obj.age, 20)

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

    def test_help_without_docstring_is_empty(self):
        class Hello(classyclick.Command):
            def __call__(self): ...

        result = self.runner.invoke(Hello.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: hello [OPTIONS]

Options:
  --help  Show this message and exit.
""",
        )

    def test_inherited_docstring_used_for_help(self):
        class BaseHello(classyclick.Command):
            """shared command help"""

            name: str = classyclick.Argument()

            def __call__(self): ...

        class Hello(BaseHello):
            pass

        result = self.runner.invoke(Hello.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: hello [OPTIONS] NAME

  shared command help

Options:
  --help  Show this message and exit.
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

    def test_config_supports_extra_click_decorators(self):
        class Hello(classyclick.Command):
            __config__ = classyclick.Command.Config(
                decorators=click.version_option(version='1.2.3', message='%(version)s'),
            )

            def __call__(self): ...

        help_result = self.runner.invoke(Hello.click, args=['--help'])
        self.assertEqual(help_result.exit_code, 0)
        self.assertIn('--version  Show the version and exit.', help_result.output)

        version_result = self.runner.invoke(Hello.click, args=['--version'])
        self.assertEqual(version_result.exit_code, 0)
        self.assertEqual(version_result.output, '1.2.3\n')

    def test_subclassing(self):
        class Hello(classyclick.Command):
            """command one"""

            name: str = classyclick.Argument()

            def __call__(self):
                print(f'Hello {self.name}')

        class Bye(Hello):
            """command two"""

            silent: bool = classyclick.Option(help='Just wave')

            def __call__(self):
                if self.silent:
                    print(':wave:')
                else:
                    print(f'Bye {self.name}')

        result = self.runner.invoke(Hello.click, ['--help'])
        self.assertEqual(
            result.output,
            """\
Usage: hello [OPTIONS] NAME

  command one

Options:
  --help  Show this message and exit.
""",
        )
        result = self.runner.invoke(Hello.click, ['John'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello John\n')

        result = self.runner.invoke(Bye.click, ['--help'])
        self.assertEqual(
            result.output,
            """\
Usage: bye [OPTIONS] NAME

  command two

Options:
  --silent  Just wave
  --help    Show this message and exit.
""",
        )
        result = self.runner.invoke(Bye.click, ['John'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Bye John\n')
