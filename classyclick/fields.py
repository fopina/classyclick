from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, get_args, get_origin

if TYPE_CHECKING:
    from dataclasses import Field

    import click
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
    return ClassyOption(param_decls=param_decls, default_parameter=default_parameter, attrs=attrs)


def argument(*, type=None, **attrs: Any) -> 'ClassyArgument':
    """
    Attaches an argument to the class field.

    Same goal as :meth:`click.argument` (see https://click.palletsprojects.com/en/latest/api/#click.Argument) decorator,
    but no parameters are needed: field name is used as name of the argument.
    """
    if type is not None:
        attrs['type'] = type
    return ClassyArgument(attrs=attrs)


def context() -> 'ClassyContext':
    """
    ...
    """
    return ClassyContext(attrs=None)


def context_obj() -> 'ClassyContextObj':
    """
    ...
    """
    return ClassyContextObj(attrs=None)


def context_meta(key: str, **attrs: Any) -> 'ClassyContextMeta':
    """
    ...
    """
    return ClassyContextMeta(key=key, attrs=attrs)


@dataclass(frozen=True)
class ClassyField:
    attrs: dict[Any]

    def infer_type(self, field: 'Field'):
        if 'type' not in self.attrs:
            if (self.attrs.get('multiple', False) or self.attrs.get('nargs', 1) > 1) and get_origin(field.type) is list:
                self.attrs['type'] = get_args(field.type)[0]
            else:
                self.attrs['type'] = field.type

    @property
    def click(self) -> 'click':
        # delay click import
        import click

        return click

    def __call__(self, command: 'Command', field: 'Field'):
        """To be implemented in subclasses"""
        return command


@dataclass(frozen=True)
class ClassyArgument(ClassyField):
    def __call__(self, command: 'Command', field: 'Field'):
        self.infer_type(field)

        return self.click.argument(field.name, **self.attrs)(command)


@dataclass(frozen=True)
class ClassyOption(ClassyField):
    param_decls: list[str]
    default_parameter: bool

    def __call__(self, command: 'Command', field: 'Field'):
        for param in self.param_decls:
            if param[0] != '-':
                raise TypeError(f'{command.__name__} option {field.name}: do not specify a name, it is already added')

        # bake field.name as option name
        param_decls = (field.name,) + self.param_decls

        if self.default_parameter:
            long_name = f'--{utils.snake_kebab(field.name)}'
            if long_name not in self.param_decls:
                param_decls = (long_name,) + param_decls

        self.infer_type(field)

        if self.attrs['type'] is bool and 'is_flag' not in self.attrs:
            # drop explicit type because of bug in click 8.2.0
            # https://github.com/pallets/click/issues/2894 / https://github.com/pallets/click/pull/2829
            del self.attrs['type']
            self.attrs['is_flag'] = True

        return self.click.option(*param_decls, **self.attrs)(command)


@dataclass(frozen=True)
class ClassyContext(ClassyField):
    def store_field_name(self, command: 'Command', field: 'Field'):
        if not hasattr(command, '__classy_context__'):
            command.__classy_context__ = []  # type: ignore
        command.__classy_context__.insert(0, field.name)

    def __call__(self, command: 'Command', field: 'Field'):
        self.store_field_name(command, field)
        return self.click.pass_context(command)


@dataclass(frozen=True)
class ClassyContextObj(ClassyContext):
    def __call__(self, command: 'Command', field: 'Field'):
        self.store_field_name(command, field)
        return self.click.pass_obj(command)


@dataclass(frozen=True)
class ClassyContextMeta(ClassyContext):
    key: str

    def __call__(self, command: 'Command', field: 'Field'):
        self.store_field_name(command, field)
        return self.click.decorators.pass_meta_key(self.key, **self.attrs)(command)
