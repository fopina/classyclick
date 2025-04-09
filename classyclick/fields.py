from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dataclasses import Field

    from click import Command

from . import utils


def option(*param_decls: str, default_parameter=True, **attrs: Any) -> 'ClassyOption':
    """
    Attaches an option to the class field.

    Similar to :meth:`click.option` (see https://click.palletsprojects.com/en/latest/api/#click.Option) decorator, except for `default_parameter`.

    `param_decls` and `attrs` will be forwarded to `click.option`
    Changes done to these:
    * An extra parameter to `param_decls` when `default_parameter` is true, based on kebab-case of the field name
      * If the field (this option is attached to) is named `dry_run`, `default_parameter` will automatically add `--dry-run` to its `param_decls`
    * Type based type hint, if none is specified
    * No "name" is allowed, as that's already infered from field.name - that means the only positional arguments allowed are the ones that start with "-"
    """
    return ClassyOption(param_decls, default_parameter, attrs)


def argument(*, type=None, **attrs: Any) -> 'ClassyArgument':
    """
    Attaches an argument to the class field.

    Same goal as :meth:`click.argument` (see https://click.palletsprojects.com/en/latest/api/#click.Argument) decorator,
    but no parameters are needed: field name is used as name of the argument.
    """
    if type is not None:
        attrs['type'] = type
    return ClassyArgument(attrs)


class ClassyField:
    def __call__(self, command: 'Command', field: 'Field'):
        """To be implemented in subclasses"""


@dataclass(frozen=True)
class ClassyArgument(ClassyField):
    attrs: dict[Any]

    def __call__(self, command: 'Command', field: 'Field'):
        # delay click import
        import click

        if 'type' not in self.attrs:
            self.attrs['type'] = field.type
        click.argument(field.name, **self.attrs)(command)


@dataclass(frozen=True)
class ClassyOption(ClassyField):
    param_decls: list[str]
    default_parameter: bool
    attrs: dict[Any]

    def __call__(self, command: 'Command', field: 'Field'):
        # delay click import
        import click

        for param in self.param_decls:
            if param[0] != '-':
                raise TypeError(
                    f'{command.classy.__module__}.{command.classy.__qualname__} option {field.name}: do not specify a name, it is already added'
                )

        # bake field.name as option name
        param_decls = (field.name,) + self.param_decls

        if self.default_parameter:
            long_name = f'--{utils.snake_kebab(field.name)}'
            if long_name not in self.param_decls:
                param_decls = (long_name,) + param_decls

        if 'type' not in self.attrs:
            self.attrs['type'] = field.type

        if self.attrs['type'] is bool and 'is_flag' not in self.attrs:
            self.attrs['is_flag'] = True

        click.option(*param_decls, **self.attrs)(command)
