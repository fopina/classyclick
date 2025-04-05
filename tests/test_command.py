import classyclick
from tests import BaseCase


class Test(BaseCase):
    def test_error(self):
        def not_a_class():
            @classyclick.command()
            def hello():
                pass

        self.assertRaisesRegex(ValueError, 'hello is not a class', not_a_class)
