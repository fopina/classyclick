
from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
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

        runner = CliRunner()

        result = runner.invoke(Hello.click, ['John'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello John, gratz on being 10\n')

        with self.assertRaisesRegex(TypeError, "missing 1 required positional argument: 'name'"):
            Hello()
        obj = Hello(name='John')
        self.assertEqual(obj.name, 'John')
        self.assertEqual(obj.age, 10)
