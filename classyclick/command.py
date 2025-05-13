from dataclasses import dataclass, fields
from typing import Callable, Protocol, TypeVar, Union

from . import utils
from .fields import ClassyField

T = TypeVar('T')


class Clickable(Protocol):
    """to merge with wrapped classed for type hints"""

    def click() -> Callable: ...


def command(group=None, **click_kwargs):
    if group is None:
        # delay import until required
        import click

        group = click

    def _wrapper(kls: T) -> Union[T, Clickable]:
        if not hasattr(kls, '__bases__'):
            name = getattr(kls, '__name__', str(kls))
            raise ValueError(f'{name} is not a class - classy stands for classes! Use @click.command instead?')

        if 'name' not in click_kwargs:
            # similar to https://github.com/pallets/click/blob/5dd628854c0b61bbdc07f22004c5da8fa8ee9481/src/click/decorators.py#L243C24-L243C60
            # click expect snake_case function names and converts to kebab-case CLI-friendly names
            # here, we expect CamelCase class names
            click_kwargs['name'] = utils.camel_kebab(kls.__name__)

        def func(*args, **kwargs):
            if args:
                args = list(args)
                ctx = getattr(func, '__classy_context__', [])
                for field_name in ctx:
                    kwargs[field_name] = args.pop()
            kls(*args, **kwargs)()

        func.__doc__ = kls.__doc__
        func.__name__ = click_kwargs['name']

        # at the end so it doesn't affect __doc__ or others
        _strictly_typed_dataclass(kls)

        # apply options
        # apply in reverse order to match click's behavior - it DOES MATTER when multiple click.argument
        for field in fields(kls)[::-1]:
            if isinstance(field.default, ClassyField):
                func = field.default(func, field)

        command = group.command(**click_kwargs)(func)

        kls.click = command

        return kls

    return _wrapper


def _strictly_typed_dataclass(kls):
    annotations = getattr(kls, '__annotations__', {})
    for name, val in kls.__dict__.items():
        if name.startswith('__'):
            continue
        if name not in annotations and isinstance(val, ClassyField):
            raise TypeError(f"{kls.__module__}.{kls.__qualname__} is missing type for classy field '{name}'")
    return dataclass(kls)
