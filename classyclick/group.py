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


def _normalize_click_decorators(decorators):
    if decorators is None:
        return ()
    if callable(decorators):
        return (decorators,)
    return tuple(decorators)


def _build_click_class_command(cls, *, is_group=False):
    doc = utils.get_inherited_doc(cls)
    utils.strictly_typed_dataclass(cls)

    group_config = _get_base_group_config(cls)
    show_envvar = getattr(group_config, '__classyclick_show_envvar__', None)
    if is_group:
        configured_show_envvar = getattr(cls.__config__, 'show_envvar', None) if cls.__config__ else None
        if configured_show_envvar is not None:
            show_envvar = configured_show_envvar
        cls.__classyclick_show_envvar__ = show_envvar

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
            if isinstance(field, Option) and show_envvar is not None and 'show_envvar' not in field.attrs:
                field.attrs['show_envvar'] = show_envvar
                try:
                    func = field(func)
                finally:
                    del field.attrs['show_envvar']
            else:
                func = field(func)

    click_kwargs = {}
    if cls.__config__:
        click_kwargs.update(vars(cls.__config__))

    for name, value in cls.__dict__.items():
        if name.startswith('__click_') and name.endswith('__'):
            key = name[len('__click_') : -2]
            if key and key not in click_kwargs:
                click_kwargs[key] = value

    click_decorators = _normalize_click_decorators(click_kwargs.pop('decorators', None))
    click_kwargs.pop('show_envvar', None)

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
    for decorator in click_decorators:
        cls.__command__ = decorator(cls.__command__)
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
        def __init__(
            self,
            *,
            name: str = None,
            help: str = None,
            decorators=None,
            auto_envvar_prefix: str = None,
            show_envvar: bool = None,
            **kwargs,
        ):
            if auto_envvar_prefix is not None:
                context_settings = dict(kwargs.pop('context_settings', None) or {})
                context_settings['auto_envvar_prefix'] = auto_envvar_prefix
                kwargs['context_settings'] = context_settings

            # Click keeps show_envvar per-option (see pallets/click#2313).
            # Classyclick offers it as a group default for options in this group.
            self.__dict__.update(
                name=name,
                help=help,
                decorators=decorators,
                show_envvar=show_envvar,
                **kwargs,
            )

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
