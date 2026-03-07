# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

# README +++
import click

import classyclick

from .cli_hello import Hello


@classyclick.command()
class Bye(Hello):
    """Simple program that says bye to NAME for a total of COUNT times."""

    def greet(self):
        for _ in range(self.count):
            click.echo(f'Bye, {self.reversed_name}!')


# README ---

if __name__ == '__main__':
    Bye.click()
