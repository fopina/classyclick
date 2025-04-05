from dataclasses import dataclass


def argument() -> 'ClassyArgument':
    """
    Attaches an argument to the class field.

    Same goal as :meth:`click.argument` (see https://click.palletsprojects.com/en/latest/api/#click.Argument) decorator,
    but no parameters are needed: field name is used as name of the argument.
    """
    return ClassyArgument()


@dataclass(frozen=True)
class ClassyArgument:
    def __call__(self, command, field_name):
        # delay click import
        import click

        click.argument(field_name)(command)
