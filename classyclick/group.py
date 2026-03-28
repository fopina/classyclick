from dataclasses import fields

import click

from . import utils
from .fields import Argument, Context, ContextMeta, ContextObj, Option, _Field


def _get_base_group_config(cls):
    for base in cls.__mro__[1:]:
        group = getattr(base, '__group_config__', None)
        if group is not None:
            return group
    return None


def _build_click_class_command(cls, *, is_group=False):
    doc = utils.get_inherited_doc(cls)
    utils.strictly_typed_dataclass(cls)

    def func(*args, **kwargs):
        if args:
            args = list(args)
            ctx = getattr(func, '__classy_context__', [])
            for field_name in ctx:
                kwargs[field_name] = args.pop()
        cls(*args, **kwargs)()

    func.__doc__ = doc
    func.__name__ = utils.camel_snake(cls.__name__)

    for field in fields(cls)[::-1]:
        if isinstance(field, _Field):
            func = field(func)

    click_kwargs = {}
    if cls.__config__:
        click_kwargs.update(vars(cls.__config__))

    for name, value in cls.__dict__.items():
        if name.startswith('__click_') and name.endswith('__'):
            key = name[len('__click_') : -2]
            if key and key not in click_kwargs:
                click_kwargs[key] = value

    click_group = click_kwargs.pop('group', None)
    if click_group is None:
        click_group = _get_base_group_config(cls)
    if click_group is None:
        click_group = click
    if isinstance(click_group, type) and issubclass(click_group, Group):
        click_group = click_group.click
    if is_group:
        cls.__group_config__ = cls
        cls.__command__ = click_group.group(**click_kwargs)(func)
    else:
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

        # Internal helper bases can carry bound group config without registering
        # themselves as real click groups.
        if cls.__dict__.get('__classyclick_skip_build__', False):
            return

        cls._build_click_group()
        cls._bind_children()

    @classmethod
    def _build_click_group(cls):
        _build_click_class_command(cls, is_group=True)

    @classmethod
    def _bind_children(cls):
        class CommandMixin:
            __group_config__ = cls

        class SubGroupMixin:
            __group_config__ = cls

        from .command import Command as BaseCommand

        class Command(CommandMixin, BaseCommand):
            __classyclick_skip_build__ = True

        class SubGroup(SubGroupMixin, Group):
            __classyclick_skip_build__ = True

        cls.CommandMixin = CommandMixin
        cls.SubGroupMixin = SubGroupMixin
        cls.Command = Command
        cls.SubGroup = SubGroup

    def __call__(self):
        """placeholder as many groups will not need anything"""
