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

    `param_decls` and `attrs` will be forwarded unchanged to `click.option`
    except for adding an extra parameter to `param_decls` when `default_parameter` is true.
    If the field (this option is attached to) is named `dry_run`, `default_parameter` will automatically add
    `--dry-run` to its `param_decls`.
    """
    return ClassyOption(param_decls, default_parameter, attrs)


def argument() -> 'ClassyArgument':
    """
    Attaches an argument to the class field.

    Same goal as :meth:`click.argument` (see https://click.palletsprojects.com/en/latest/api/#click.Argument) decorator,
    but no parameters are needed: field name is used as name of the argument.
    """
    return ClassyArgument()


class ClassyField:
    def __call__(self, command: 'Command', field: 'Field'):
        """To be implemented in subclasses"""


@dataclass(frozen=True)
class ClassyArgument(ClassyField):
    def __call__(self, command: 'Command', field: 'Field'):
        # delay click import
        import click

        click.argument(field.name, type=field.type)(command)


@dataclass(frozen=True)
class ClassyOption(ClassyField):
    param_decls: list[str]
    default_parameter: bool
    attrs: dict[Any]

    def __call__(self, command: 'Command', field: 'Field'):
        # delay click import
        import click

        param_decls = self.param_decls
        if self.default_parameter:
            long_name = f'--{utils.snake_kebab(field.name)}'
            if long_name not in self.param_decls:
                param_decls = (long_name,) + self.param_decls

        if 'type' not in self.attrs:
            self.attrs['type'] = field.type

        click.option(*param_decls, **self.attrs)(command)
