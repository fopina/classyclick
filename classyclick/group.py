from dataclasses import fields

try:
    from typing import dataclass_transform
except ImportError:
    from typing_extensions import dataclass_transform

import click

from . import utils
from .command import Command, _strictly_typed_dataclass
from .fields import Argument, Context, ContextMeta, ContextObj, Option, _Field


@dataclass_transform(field_specifiers=(Option, Argument, Context, ContextObj, ContextMeta))
class Group(Command):
    """Base class for class-based click groups."""

    class Config(Command.Config):
        pass

    @classmethod
    def _build_click_command(cls):
        _strictly_typed_dataclass(cls)

        def func(*args, **kwargs):
            if args:
                args = list(args)
                ctx = getattr(func, '__classy_context__', [])
                for field_name in ctx:
                    kwargs[field_name] = args.pop()
            cls(*args, **kwargs)()

        func.__doc__ = cls.__doc__
        func.__name__ = utils.camel_snake(cls.__name__)

        for field in fields(cls)[::-1]:
            if isinstance(field, _Field):
                func = field(func)

        click_kwargs = {}
        config = getattr(cls, '__config__', None)
        if isinstance(config, Command.Config):
            click_kwargs.update(vars(config))

        for name, value in cls.__dict__.items():
            if name.startswith('__click_') and name.endswith('__'):
                key = name[len('__click_') : -2]
                if key not in click_kwargs:
                    click_kwargs[key] = value

        group = click_kwargs.pop('group', None)
        if group is None:
            group = click
        cls.__command__ = group.group(**click_kwargs)(func)
        cls.click = cls.__command__
