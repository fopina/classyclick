from dataclasses import dataclass
from typing import Any

from . import utils


def option(*param_decls: str, default_parameter=True, **attrs: Any) -> 'ClassyOption':
    """
    Attaches an option to the class field.

    Similar to `click.option` decorator, except for `default_parameter`.

    `param_decls` and `attrs` will be forwarded unchanged to `click.option`
    except for adding an extra parameter to `param_decls` when `default_parameter` is true.
    If the field (this option is attached) is name `dry_run`, `default_parameter` will automatically add
    `--dry-run` to its `param_decls`.
    """
    return ClassyOption(param_decls, default_parameter, attrs)


@dataclass(frozen=True)
class ClassyOption:
    param_decls: list[str]
    default_parameter: bool
    attrs: dict[Any]

    def __call__(self, command, field_name):
        # delay click import
        import click

        param_decls = self.param_decls
        if self.default_parameter:
            long_name = f'--{utils.snake_kebab(field_name)}'
            if long_name not in self.param_decls:
                param_decls = (long_name,) + self.param_decls
        click.option(*param_decls, **self.attrs)(command)
