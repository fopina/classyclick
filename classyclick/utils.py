import inspect
import re
from dataclasses import MISSING, dataclass, fields

from classyclick.fields import Argument, ContextMeta, Option, _Field

try:
    from typing import dataclass_transform
except ImportError:
    # for python < 3.13
    from typing_extensions import dataclass_transform  # type: ignore


def camel_kebab(camel_value):
    """
    Convert CamelCase to kebab-case
    """
    return re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', camel_value).lower()


def camel_snake(camel_value):
    """
    Convert CamelCase to snake_case
    """
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', camel_value).lower()


def snake_kebab(snake_value):
    """
    Convert snake_case to kebab-case
    """
    # wrapping simple logic just in case exceptions come along
    return snake_value.replace('_', '-')


def get_inherited_doc(kls):
    doc = inspect.getdoc(kls)
    if doc is None:
        return None

    if kls.__doc__ is not None:
        return doc

    from .command import Command
    from .group import Group

    if doc in (Command.__doc__, Group.__doc__):
        return None

    return doc


def strictly_typed_dataclass(kls):
    # Python 3.9 can expose inherited annotations via getattr(..., '__annotations__'),
    # which makes base helper attributes like `click` look like local dataclass fields.
    # Once Python 3.9 support is dropped, revisit whether this can be simplified.
    annotations = kls.__dict__.get('__annotations__', {})
    for name, val in kls.__dict__.items():
        if name.startswith('__'):
            continue
        if name not in annotations and isinstance(val, _Field):
            raise TypeError(f"{kls.__module__}.{kls.__qualname__} is missing type for classy field '{name}'")
    kls = dataclass(kls, init=False)
    _validate_local_field_order(kls)
    _build_init(kls)
    return kls


def _validate_local_field_order(kls):
    # Same Python 3.9 compatibility note as in strictly_typed_dataclass():
    # only consider annotations declared on this class body.
    local_annotations = kls.__dict__.get('__annotations__', {})
    dataclass_fields = kls.__dataclass_fields__
    previous_default = None
    for name in local_annotations:
        if name.startswith('__'):
            continue

        value = dataclass_fields[name]
        has_default = not _field_is_required_for_init(value)

        if has_default:
            previous_default = name
        elif previous_default is not None:
            raise TypeError(f"non-default argument '{name}' follows default argument '{previous_default}'")


def _build_init(kls):
    if '__init__' in kls.__dict__:
        return

    init_fields = tuple(field for field in fields(kls) if field.init)
    positional_fields = []
    for field in init_fields:
        if getattr(field, 'kw_only', False):
            continue
        positional_fields.append(field)
        if not _field_is_required_for_init(field):
            break
    positional_fields = tuple(positional_fields)

    def __init__(self, *args, **kwargs):
        if len(args) > len(positional_fields):
            raise TypeError(
                f'{kls.__name__}.__init__() takes {len(positional_fields) + 1} positional arguments '
                f'but {len(args) + 1} were given'
            )

        remaining_kwargs = dict(kwargs)
        missing = []

        for index, field in enumerate(positional_fields):
            required_for_init = _field_is_required_for_init(field)
            if index < len(args):
                value = args[index]
                if field.name in remaining_kwargs:
                    raise TypeError(f"{kls.__name__}.__init__() got multiple values for argument '{field.name}'")
            elif field.name in remaining_kwargs:
                value = remaining_kwargs.pop(field.name)
            elif required_for_init:
                # Keep init-time requiredness separate from dataclass/click defaults.
                # This is needed for older Python targets because click-backed fields do
                # not report defaults consistently across 3.9/3.10.
                missing.append(field.name)
                continue
            elif field.default is not MISSING:
                value = field.default
            elif field.default_factory is not MISSING:
                value = field.default_factory()
            else:
                missing.append(field.name)
                continue

            setattr(self, field.name, value)

        for field in init_fields[len(positional_fields) :]:
            required_for_init = _field_is_required_for_init(field)
            if field.name in remaining_kwargs:
                value = remaining_kwargs.pop(field.name)
            elif required_for_init:
                # Same cross-version compatibility path as above; drop with old-Python support.
                missing.append(field.name)
                continue
            elif field.default is not MISSING:
                value = field.default
            elif field.default_factory is not MISSING:
                value = field.default_factory()
            else:
                missing.append(field.name)
                continue

            setattr(self, field.name, value)

        if missing:
            raise TypeError(_format_missing_message(kls, missing))

        if remaining_kwargs:
            unexpected = next(iter(remaining_kwargs))
            raise TypeError(f"{kls.__name__}.__init__() got an unexpected keyword argument '{unexpected}'")

        post_init = getattr(self, '__post_init__', None)
        if post_init is not None:
            post_init()

    kls.__init__ = __init__


def _format_missing_message(kls, missing):
    count = len(missing)
    if count == 1:
        names = f"'{missing[0]}'"
    elif count == 2:
        names = f"'{missing[0]}' and '{missing[1]}'"
    else:
        names = ', '.join(f"'{name}'" for name in missing[:-1]) + f", and '{missing[-1]}'"
    return f'{kls.__name__}.__init__() missing {count} required positional argument{"s" if count != 1 else ""}: {names}'


def _field_has_python_default(field):
    if field.default_factory is not MISSING:
        return True
    if field.default is MISSING:
        return False
    return not _is_click_unset(field.default)


def _field_is_required_for_init(field):
    if isinstance(field, Option):
        # Python 3.9/3.10 differ in how click-derived defaults surface on Option fields:
        # prompted options may look like they default to None on 3.9, while plain options
        # can stay as click.UNSET on 3.10. Base requiredness on explicit user intent so this
        # branch can be removed when older Python compatibility is no longer needed.
        has_explicit_default = 'default' in field.attrs or field.default_factory is not MISSING
        if field.attrs.get('required', False):
            return not has_explicit_default
        if field.attrs.get('prompt') and not has_explicit_default:
            return True
        if _field_has_python_default(field):
            return False
        return False
    if isinstance(field, Argument):
        if _field_has_python_default(field):
            return False
        return field.attrs.get('required', True)
    if isinstance(field, ContextMeta):
        return True
    if _field_has_python_default(field):
        return False
    return field.default is MISSING and field.default_factory is MISSING


def _is_click_unset(value):
    return type(value).__module__ == 'click._utils' and type(value).__qualname__ == 'Sentinel' and value.name == 'UNSET'


__all__ = ['dataclass_transform']
