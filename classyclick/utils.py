import re


def camel_kebab(camel_value):
    """
    Convert CamelCase to kebab-case
    """
    return re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', camel_value).lower()
