from .command import _build_click_class_command, dataclass_transform
from .fields import Argument, Context, ContextMeta, ContextObj, Option


@dataclass_transform(field_specifiers=(Option, Argument, Context, ContextObj, ContextMeta))
class Group:
    """Base class for class-based click groups."""

    class Config:
        def __init__(self, *, name: str = None, help: str = None, **kwargs):
            self.__dict__.update(name=name, help=help, **kwargs)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls is Group:
            return

        cls._build_click_command()

    @classmethod
    def _build_click_command(cls):
        _build_click_class_command(cls, is_group=True)
