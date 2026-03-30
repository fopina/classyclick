#!/usr/bin/env python3
# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import click

import classyclick


# README +++
class NextGroupMeta(classyclick.Group):
    the_context: click.Context = classyclick.Context()

    def __call__(self):
        self.the_context.meta['step_number'] = 5


class Next(NextGroupMeta.Command):
    """Output the next number."""

    your_number: int = classyclick.Argument()
    step_number: int = classyclick.ContextMeta('step_number')

    def __call__(self):
        click.echo(self.your_number + self.step_number)


# README ---

next_group_meta = NextGroupMeta.click


if __name__ == '__main__':
    NextGroupMeta.click()
