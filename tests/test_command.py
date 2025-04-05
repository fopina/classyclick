from unittest import TestCase

import classyclick


class Test(TestCase):
    @property
    def click_version(self):
        from click import __version__

        return tuple(map(int, __version__.split('.')))

    def test_error(self):
        def not_a_class():
            @classyclick.command()
            def hello():
                pass

        self.assertRaisesRegex(ValueError, 'hello is not a class', not_a_class)
