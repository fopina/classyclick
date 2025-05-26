from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, Callable, Protocol, TypeVar, Union

if TYPE_CHECKING:
    from click import Command

from . import utils
from .fields import _Field

T = TypeVar('T')


class Clickable(Protocol):
    """to merge with wrapped classed for type hints"""

    click: 'Command'
    """
    Run click command
    """


def command(cls=None, *, group=None, **click_kwargs) -> Callable[[T], Union[T, Clickable]]:
    if group is None:
        # delay import until required
        import click

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
        _strictly_typed_dataclass(kls)

        # apply options
        # apply in reverse order to match click's behavior - it DOES MATTER when multiple click.argument
        for field in fields(kls)[::-1]:
            if isinstance(field, _Field):
                func = field(func, field)

        command = group.command(**click_kwargs)(func)

        kls.click = command

        return kls

    if cls is None:
        # called with parens
        return _wrapper
    return _wrapper(cls)


def _strictly_typed_dataclass(kls):
    annotations = getattr(kls, '__annotations__', {})
    for name, val in kls.__dict__.items():
        if name.startswith('__'):
            continue
        if name not in annotations and isinstance(val, _Field):
            raise TypeError(f"{kls.__module__}.{kls.__qualname__} is missing type for classy field '{name}'")
    return dataclass(kls)
