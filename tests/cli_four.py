# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import click

import classyclick


@classyclick.command()
class Next:
    """Output the next number."""

    your_number: int = classyclick.Argument()

    def __call__(self):
        click.echo(self.your_number + 1)


if __name__ == '__main__':
    Next.click()
