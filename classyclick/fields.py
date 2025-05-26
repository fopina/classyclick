from dataclasses import MISSING
from dataclasses import Field as DataclassField
from typing import TYPE_CHECKING, Any, get_args, get_origin

from typing_extensions import deprecated

if TYPE_CHECKING:
    from dataclasses import Field

    import click
    from click import Command

from . import utils


@deprecated('use Option instead')
def option(*param_decls: str, default_parameter=True, **attrs: Any) -> 'Option':
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
    return Option(*param_decls, default_parameter=default_parameter, **attrs)


@deprecated('use Argument instead')
def argument(*, type=None, **attrs: Any) -> 'Argument':
    """
    Attaches an argument to the class field.

    Same goal as :meth:`click.argument` (see https://click.palletsprojects.com/en/latest/api/#click.Argument) decorator,
    but no parameters are needed: field name is used as name of the argument.
    """
    return Argument(type=type, **attrs)


@deprecated('use Context instead')
def context() -> 'Context':
    """
    Like :meth:`click.pass_context` (see https://click.palletsprojects.com/en/stable/api/#click.pass_context),
    this exposes `click.Context` in a command property.
    """
    return Context()


@deprecated('use ContextObj instead')
def context_obj() -> 'ContextObj':
    """
    Like :meth:`click.pass_obj` (see https://click.palletsprojects.com/en/stable/api/#click.pass_obj),
    this assigns `click.Context.obj` to a command property, when you only want the user data rather than the whole context.
    """
    return ContextObj()


@deprecated('use ContextMeta instead')
def context_meta(key: str, **attrs: Any) -> 'ContextMeta':
    """
    Like :meth:`click.pass_meta_key` (see https://click.palletsprojects.com/en/stable/api/#click.decorators.pass_meta_key),
    this assigns `click.Context.meta[KEY]` to a command property, without handling the whole context.
    """
    return ContextMeta(key, **attrs)


class _Field(DataclassField):
    attrs: dict[Any]

    def __init__(self, **attrs):
        _default = attrs.get('default', MISSING)
        super().__init__(
            default=_default,
            default_factory=MISSING,
            init=True,
            repr=True,
            hash=None,
            compare=True,
            metadata=None,
            kw_only=MISSING,
        )
        self.attrs = attrs

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

    def __call__(self, command: 'Command', field: 'Field') -> 'Command':
        """To be implemented in subclasses"""


class Argument(_Field):
    """
    Attaches an argument to the class field.

    Same goal as :meth:`click.argument` (see https://click.palletsprojects.com/en/latest/api/#click.Argument) decorator,
    but no parameters are needed: field name is used as name of the argument.
    """

    def __init__(self, *, type=None, **attrs: Any):
        if type is not None:
            attrs['type'] = type
        super().__init__(**attrs)

    def __call__(self, command: 'Command', field: 'Field'):
        self.infer_type(field)

        return self.click.argument(field.name, **self.attrs)(command)


class Option(_Field):
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

    def __init__(self, *param_decls: list[str], default_parameter=True, **attrs):
        super().__init__(**attrs)
        self.param_decls = param_decls
        self.default_parameter = default_parameter

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


class Context(_Field):
    """
    Like :meth:`click.pass_context` (see https://click.palletsprojects.com/en/stable/api/#click.pass_context),
    this exposes `click.Context` in a command property.
    """

    def store_field_name(self, command: 'Command', field: 'Field'):
        if not hasattr(command, '__classy_context__'):
            command.__classy_context__ = []  # type: ignore
        command.__classy_context__.insert(0, field.name)

    def __call__(self, command: 'Command', field: 'Field'):
        self.store_field_name(command, field)
        return self.click.pass_context(command)


class ContextObj(Context):
    """
    Like :meth:`click.pass_obj` (see https://click.palletsprojects.com/en/stable/api/#click.pass_obj),
    this assigns `click.Context.obj` to a command property, when you only want the user data rather than the whole context.
    """

    def __call__(self, command: 'Command', field: 'Field'):
        self.store_field_name(command, field)
        return self.click.pass_obj(command)


class ContextMeta(Context):
    """
    Like :meth:`click.pass_meta_key` (see https://click.palletsprojects.com/en/stable/api/#click.decorators.pass_meta_key),
    this assigns `click.Context.meta[KEY]` to a command property, without handling the whole context.
    """

    def __init__(self, key: str, **attrs):
        super().__init__(**attrs)
        self.key = key

    def __call__(self, command: 'Command', field: 'Field'):
        self.store_field_name(command, field)
        return self.click.decorators.pass_meta_key(self.key, **self.attrs)(command)
