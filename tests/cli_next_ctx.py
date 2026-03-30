#!/usr/bin/env python3
# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path
from types import SimpleNamespace

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

next_group = NextGroup.click


if __name__ == '__main__':
    NextGroup.click()
