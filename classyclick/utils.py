import ast
import inspect
import re
import textwrap
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


def get_attribute_docstrings(kls):
    try:
        source = textwrap.dedent(inspect.getsource(kls))
    except (OSError, TypeError):
        return {}

    try:
        module = ast.parse(source)
    except SyntaxError:
        return {}

    class_def = next(
        (node for node in module.body if isinstance(node, ast.ClassDef) and node.name == kls.__name__),
        None,
    )
    if class_def is None:
        return {}

    docs = {}
    for node, next_node in zip(class_def.body, class_def.body[1:]):
        if not (
            isinstance(next_node, ast.Expr)
            and isinstance(next_node.value, ast.Constant)
            and isinstance(next_node.value.value, str)
        ):
            continue

        name = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id

        if name is not None:
            docs[name] = inspect.cleandoc(next_node.value.value)

    return docs


def apply_field_help_from_attribute_docstrings(kls):
    docstrings = get_attribute_docstrings(kls)
    for name, val in kls.__dict__.items():
        if name.startswith('__') or not isinstance(val, _Field):
            continue
        if 'help' not in val.attrs and name in docstrings:
            val.attrs['help'] = docstrings[name]


__all__ = ['dataclass_transform']
