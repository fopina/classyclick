from unittest import TestCase

from classyclick import command


class Test(TestCase):
    def test_error(self):
        def not_a_class():
            @command()
            def hello():
                pass

        self.assertRaises(ValueError, not_a_class)
