from dataclasses import dataclass, fields

from . import utils
from .fields import ClassyArgument, ClassyOption


def command(group=None, **click_kwargs):
    if group is None:
        # delay import until required
        import click

        group = click

    def _wrapper(kls):
        if not hasattr(kls, '__bases__'):
            name = getattr(kls, '__name__', str(kls))
            raise ValueError(f'{name} is not a class - classy stands for classes! Use @click.command instead?')

        if 'name' not in click_kwargs:
            # similar to https://github.com/pallets/click/blob/5dd628854c0b61bbdc07f22004c5da8fa8ee9481/src/click/decorators.py#L243C24-L243C60
            # click expect snake_case function names and converts to kebab-case CLI-friendly names
            # here, we expect CamelCase class names
            click_kwargs['name'] = utils.camel_kebab(kls.__name__)

        def func(**args):
            kls(**args)()

        func.__doc__ = kls.__doc__
        # deprecated: reference moved to `Command.classy` instead to be more accessible (than `Command.callback._classy_`)
        func._classy_ = kls

        # at the end so it doesn't affect __doc__ or others
        _strictly_typed_dataclass(kls)
        command = group.command(**click_kwargs)(func)
        command.classy = kls

        # apply options
        for field in fields(kls):
            if isinstance(field.default, ClassyOption):
                field.default(command, field)
            elif isinstance(field.default, ClassyArgument):
                field.default(command, field)

        return command

    return _wrapper


def _strictly_typed_dataclass(kls):
    annotations = getattr(kls, '__annotations__', {})
    for name, val in kls.__dict__.items():
        if name.startswith('__'):
            continue
        if name not in annotations and isinstance(val, (ClassyArgument, ClassyOption)):
            raise TypeError(f"{kls.__module__}.{kls.__qualname__} is missing type for option/argument '{name}'")
    return dataclass(kls)
