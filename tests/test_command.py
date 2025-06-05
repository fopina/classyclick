import inspect

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

    def test_dataclass_typehints(self):
        @classyclick.command
        class Hello:
            """test command docstring"""

            name: str = classyclick.Argument()
            age: int = classyclick.Option(default=10)

            def __call__(self):
                """x"""
                print(f'Hello {self.name}, gratz on being {self.age}')

            def other_method(self):
                """y"""
                return 2

        with self.assertRaisesRegex(TypeError, "missing 1 required positional argument: 'name'"):
            Hello()

        self.assertEqual(Hello('x').age, 10)
        self.assertEqual(Hello('x').other_method(), 2)
        self.assertEqual(str(inspect.signature(Hello)), '(name: str, age: int = 10) -> None')
        self.assertEqual(inspect.cleandoc(Hello.__doc__), 'test command docstring')
