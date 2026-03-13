from dataclasses import fields

import click

from . import utils
from .fields import Argument, Context, ContextMeta, ContextObj, Option, _Field


def _get_base_config(cls):
    for base in cls.__mro__[1:]:
        if '__config__' in base.__dict__:
            config = base.__dict__['__config__']
            if config is not None:
                return config
        if '__group_config__' in base.__dict__:
            group_config = base.__dict__['__group_config__']
            if isinstance(group_config, type):
                if '__config__' in group_config.__dict__:
                    config = group_config.__dict__['__config__']
                    if config is not None:
                        return config
            elif getattr(group_config, '__dict__', None) and group_config is not None:
                return group_config
    return None


def _get_base_group(cls):
    for base in cls.__mro__[1:]:
        if '__group_config__' not in base.__dict__:
            continue
        group_ref = base.__dict__['__group_config__']
        if group_ref is None:
            continue
        if isinstance(group_ref, type) and issubclass(group_ref, Group):
            return group_ref
        if getattr(group_ref, '__dict__', None):
            return getattr(group_ref, 'group', group_ref)
    return None


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
    config = cls.__dict__.get('__config__')
    if config is None:
        config = _get_base_config(cls)
    if getattr(config, '__dict__', None):
        click_kwargs.update(vars(config))

    for name, value in cls.__dict__.items():
        if name.startswith('__click_') and name.endswith('__'):
            key = name[len('__click_') : -2]
            if key and key not in click_kwargs:
                click_kwargs[key] = value

    click_group = click_kwargs.pop('group', None)
    if click_group is None:
        click_group = _get_base_group(cls)
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

        cls._build_click_command()

    @classmethod
    def _build_click_command(cls):
        _build_click_class_command(cls, is_group=True)

    def __call__(self):
        """placeholder as many groups will not need anything"""
