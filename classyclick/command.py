from dataclasses import fields
from typing import Callable, Protocol, TypeVar, Union

import click

from . import utils
from .fields import Argument, Context, ContextMeta, ContextObj, Option, _Field
from .group import _build_click_class_command

T = TypeVar('T')


class Clickable(Protocol):
    """to merge with wrapped classed for type hints"""

    click: 'click.Command'
    """
    Run click command
    """


def command(cls=None, *, group=None, **click_kwargs) -> Callable[[T], Union[T, Clickable]]:
    if group is None:
        group = click

    def _wrapper(kls: T) -> Union[T, Clickable]:
        if not hasattr(kls, '__bases__'):
            name = getattr(kls, '__name__', str(kls))
            raise ValueError(f'{name} is not a class - classy stands for classes! Use @click.command instead?')

        def func(*args, **kwargs):
            if args:
                args = list(args)
                ctx = getattr(func, '__classy_context__', [])
                for field_name in ctx:
                    kwargs[field_name] = args.pop()
            kls(*args, **kwargs)()

        func.__doc__ = kls.__doc__
        # To re-use click logic (https://github.com/pallets/click/blob/fd183b2ced1cb5857784fe7fb22f4982f671f098/src/click/decorators.py#L242)
        # convert camel to snake as function name and let click itself convert to kebab (and trim whatever it wants) if custom 'name' is not specified
        func.__name__ = utils.camel_snake(kls.__name__)

        # at the end so it doesn't affect __doc__ or others
        utils.strictly_typed_dataclass(kls)

        # apply options
        # apply in reverse order to match click's behavior - it DOES MATTER when multiple click.argument
        for field in fields(kls)[::-1]:
            if isinstance(field, _Field):
                func = field(func)

        command = group.command(**click_kwargs)(func)

        kls.click = command

        return kls

    if cls is None:
        # called with parens
        return _wrapper
    return _wrapper(cls)


@utils.dataclass_transform(field_specifiers=(Option, Argument, Context, ContextObj, ContextMeta))
class Command:
    """Base class for class-based click commands."""

    __config__: 'Config | None' = None
    """
    Customize the command with click arguments setting this to a classyclick.Command.Config instance
    """

    class Config:
        def __init__(self, *, name: str = None, help: str = None, group: 'click.Group' = None, **kwargs):
            self.__dict__.update(name=name, help=help, group=group, **kwargs)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls is Command:
            return

        cls._build_click_command()

    @classmethod
    def _build_click_command(cls):
        _build_click_class_command(cls, is_group=False)
