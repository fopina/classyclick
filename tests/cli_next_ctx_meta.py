#!/usr/bin/env python3
# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import click

import classyclick


# README +++
@click.group()
@click.pass_context
def next_group(ctx):
    ctx.meta['step_number'] = 5


@classyclick.command(group=next_group)
class Next:
    """Output the next number."""

    your_number: int = classyclick.Argument()
    step_number: int = classyclick.ContextMeta('step_number')

    def __call__(self):
        click.echo(self.your_number + self.step_number)


# README ---

if __name__ == '__main__':
    next_group()
