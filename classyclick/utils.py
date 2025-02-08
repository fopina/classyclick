import re


def camel_kebab(camel_value):
    """
    Convert CamelCase to kebab-case
    """
    return re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', camel_value).lower()


def snake_kebab(snake_value):
    """
    Convert snake_case to kebab-case
    """
    # wrapping simple logic just in case exceptions come along
    return snake_value.replace('_', '-')
