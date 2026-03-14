import re
from dataclasses import dataclass

from classyclick.fields import _Field

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


def strictly_typed_dataclass(kls):
    annotations = getattr(kls, '__annotations__', {})
    for name, val in kls.__dict__.items():
        if name.startswith('__'):
            continue
        if name not in annotations and isinstance(val, _Field):
            raise TypeError(f"{kls.__module__}.{kls.__qualname__} is missing type for classy field '{name}'")
    return dataclass(kls)


__all__ = ['dataclass_transform']
