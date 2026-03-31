import classyclick
from tests import BaseCase


class Test(BaseCase):
    def test_subclassing_argument_after_base_option_raises_dataclass_error(self):
        """https://github.com/fopina/classyclick/issues/34"""

        class Base(classyclick.Command):
            base_arg: str = classyclick.Argument()
            base_opt: str = classyclick.Option()

            def __call__(self): ...

        with self.assertRaisesRegex(TypeError, "non-default argument 'child_arg' follows default argument 'base_opt'"):

            class Child(Base):
                child_arg: str = classyclick.Argument()
                child_opt: str = classyclick.Option()

                def __call__(self): ...
