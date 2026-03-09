#!/usr/bin/env python3
# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).parent.parent))

import click

import classyclick


# README +++
@classyclick.command()
class Next:
    """Output the next number."""

    your_number: int = classyclick.Argument()
    the_context: Any = classyclick.Context()

    def __call__(self):
        click.echo(self.your_number + self.the_context.obj.step_number)


# README ---

if __name__ == '__main__':
    Next.click()
