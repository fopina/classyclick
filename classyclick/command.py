from dataclasses import fields
import click

from .group import _build_click_class_command
from . import utils
from .fields import Argument, Context, ContextMeta, ContextObj, Option


@utils.dataclass_transform(field_specifiers=(Option, Argument, Context, ContextObj, ContextMeta))
class Command:
    """Base class for class-based click commands."""

    __config__: 'Config | None' = None
    """
    Customize the command with click arguments setting this to a classyclick.Command.Config instance
    """
    click: 'click.Command'
    """
    The generated click.Command object
    """

    class Config:
        def __init__(
            self,
            *,
            name: str = None,
            help: str = None,
            group: 'click.Group' = None,
            decorators=None,
            **kwargs,
        ):
            self.__dict__.update(name=name, help=help, group=group, decorators=decorators, **kwargs)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls is Command:
            return

        # Internal helper bases can opt out of immediate click wiring while still
        # letting concrete subclasses inherit the normal Command behavior.
        if cls.__dict__.get('__classyclick_skip_build__', False):
            return

        if '__call__' not in cls.__dict__ and not any(
            '__call__' in getattr(base, '__dict__', {}) for base in cls.__mro__[1:] if base is not Command
        ):
            raise NotImplementedError(f'{cls} has not implemented __call__()')

        cls._build_click_command()

    @classmethod
    def _build_click_command(cls):
        _build_click_class_command(cls, is_group=False)
