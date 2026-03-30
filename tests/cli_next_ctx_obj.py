#!/usr/bin/env python3
# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).parent.parent))

import click
from cli_next_ctx import NextGroup, next_group

import classyclick


# README +++
class Next(NextGroup.Command):
    """Output the next number."""

    your_number: int = classyclick.Argument()
    the_context: Any = classyclick.ContextObj()

    def __call__(self):
        click.echo(self.your_number + self.the_context.step_number)


# README ---


@classyclick.command(group=next_group)
class Next:
    """Output the next number."""

    your_number: int = classyclick.Argument()
    the_context: Any = classyclick.ContextObj()

    def __call__(self):
        click.echo(self.your_number + self.the_context.step_number)


if __name__ == '__main__':
    next_group()
