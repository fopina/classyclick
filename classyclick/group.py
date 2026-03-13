from dataclasses import fields

import click

from . import utils
from .fields import Argument, Context, ContextMeta, ContextObj, Option, _Field


def _build_click_class_command(cls, *, is_group=False):
    utils.strictly_typed_dataclass(cls)

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
    if getattr(config, '__dict__', None):
        click_kwargs.update(vars(config))

    for name, value in cls.__dict__.items():
        if name.startswith('__click_') and name.endswith('__'):
            key = name[len('__click_') : -2]
            if key and key not in click_kwargs:
                click_kwargs[key] = value

    click_group = click_kwargs.pop('group', None)
    if click_group is None:
        click_group = click
    if is_group:
        cls.__command__ = click_group.group(**click_kwargs)(func)
    else:
        if isinstance(click_group, type) and issubclass(click_group, Group):
            click_group = click_group.click
        cls.__command__ = click_group.command(**click_kwargs)(func)
    cls.click = cls.__command__


@utils.dataclass_transform(field_specifiers=(Option, Argument, Context, ContextObj, ContextMeta))
class Group:
    """Base class for class-based click groups."""

    __config__: 'Config | None' = None
    """
    Customize the group with click arguments setting this to a classyclick.Group.Config instance
    """
    click: 'click.Group'
    """
    The generated click.Group object
    """

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

    def __call__(self):
        """placeholder as many groups will not need anything"""
