#!/usr/bin/env python3
# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.append(str(Path(__file__).parent.parent))

import click

import classyclick


# README +++
class NextGroup(classyclick.Group):
    the_context: click.Context = classyclick.Context()

    def __call__(self):
        self.the_context.obj = SimpleNamespace(step_number=4)


class Next(NextGroup.Command):
    """Output the next number."""

    your_number: int = classyclick.Argument()
    the_context: click.Context = classyclick.Context()

    def __call__(self):
        click.echo(self.your_number + self.the_context.obj.step_number)


# README ---


@click.group()
@click.pass_context
def next_group(ctx):
    ctx.obj = SimpleNamespace(step_number=4)


@classyclick.command(group=next_group)
class Next:  # noqa: F811 - remove all these overrides (because of non-reversing demos?) in future PR
    """Output the next number."""

    your_number: int = classyclick.Argument()
    the_context: Any = classyclick.Context()

    def __call__(self):
        click.echo(self.your_number + self.the_context.obj.step_number)


if __name__ == '__main__':
    next_group()
