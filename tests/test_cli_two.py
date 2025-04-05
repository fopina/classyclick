from unittest import TestCase


class Test(TestCase):
    def test_hello(self):
        def _a():
            from .cli_two import Hello

            # no-op until "ruff format" gets pragma support (like # fmt: off)
            Hello

        self.assertRaisesRegex(TypeError, "tests.cli_two.Hello is missing type for option/argument 'name'", _a)
