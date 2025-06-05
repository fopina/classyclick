import sys
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


_EXTRA_DATACLASS_INIT = dict(default_factory=MISSING, init=True, repr=True, hash=None, compare=True, metadata=None)
if sys.version_info >= (3, 10):
    _EXTRA_DATACLASS_INIT['kw_only'] = MISSING


class _Field(DataclassField):
    attrs: dict[Any]
    _click_type = MISSING
    # it is set in Field.__init__ but set it first, as `set_type` will be called before it is initialized in Field.__init__
    default = MISSING

    def __init__(self, **attrs):
        self.attrs = attrs
        _default = attrs.get('default', self.default)
        super().__init__(default=_default, **_EXTRA_DATACLASS_INIT)

    def infer_type(self, field: 'Field'):
        if 'type' not in self.attrs:
            if (self.attrs.get('multiple', False) or self.attrs.get('nargs', 1) > 1) and get_origin(field.type) is list:
                self.attrs['type'] = get_args(field.type)[0]
            else:
                self.attrs['type'] = field.type

    def get_type(self):
        return self._click_type

    def set_type(self, val):
        changed = self._click_type != val
        self._click_type = val
        if self.default is MISSING and changed:
            self._click_update_dataclass_default()

    # VERY HACKY ALERT
    # Wrap Field.type with a setter to be able to catch it, calculate click default value (which changes based on type) and reset it for the dataclass Field
    # this relies on the fact that dataclasses._get_field sets Field.type before reading Field.default...!
    # https://github.com/python/cpython/blob/f690a6f1c2199a075ceb49a6b583143ed6cafb5b/Lib/dataclasses.py#L689
    # This needs to be covered heavily by unit tests
    type = property(get_type, set_type)

    def _click_update_dataclass_default(self):
        """to be implemented by each class, defaults to no action"""

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

    This is a REQUIRED value, unless you set required=False. Make sure to declare it appropriately: required fields declared always before optional fields.
    """

    def __init__(self, *, type=None, **attrs: Any):
        if type is not None:
            attrs['type'] = type
        super().__init__(**attrs)

    def __call__(self, command: 'Command', field: 'Field'):
        self.infer_type(field)

        return self.click.argument(field.name, **self.attrs)(command)

    def _click_update_dataclass_default(self):
        o = _FakeCommand()
        self.click.argument('x', **self.attrs)(o)
        if o.param.default is MISSING and not o.param.required:
            self.default = None
        return super()._click_update_dataclass_default()


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

    This is an OPTIONAL value, unless you set required=True. Make sure to declare it appropriately: required fields declared always before optional fields.
    """

    default = None

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
    This is an OPTIONAL value (declare it after required ones)
    """

    # in click, it is always set to something - for dataclass use, let's just set it to None for now
    default = None

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
    This is an OPTIONAL value (declare it after required ones)
    """

    # in click, default ctx.obj is None (and there is always a ctx) - so default to None for dataclass
    default = None

    def __call__(self, command: 'Command', field: 'Field'):
        self.store_field_name(command, field)
        return self.click.pass_obj(command)


class ContextMeta(Context):
    """
    Like :meth:`click.pass_meta_key` (see https://click.palletsprojects.com/en/stable/api/#click.decorators.pass_meta_key),
    this assigns `click.Context.meta[KEY]` to a command property, without handling the whole context.
    This is a REQUIRED value (declare it before optional ones)
    """

    # in click, non-existent key throws KeyError, so make this a required dataclass field
    default = MISSING

    def __init__(self, key: str, **attrs):
        super().__init__(**attrs)
        self._ctx_meta_key = key

    def __call__(self, command: 'Command', field: 'Field'):
        self.store_field_name(command, field)
        return self.click.decorators.pass_meta_key(self._ctx_meta_key, **self.attrs)(command)


class _FakeCommand:
    """used to be able to extract param_memo from click argument/option calls..."""

    def __init__(self):
        self.__click_params__ = []

    @property
    def param(self):
        return self.__click_params__[0]
