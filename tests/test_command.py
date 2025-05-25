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

        # self.assertEqual(HelloThereCommand.click.name, 'hello-there')
