# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import click

import classyclick
from tests.cli_one import Hello


@classyclick.command()
class Bye(Hello.classy):
    """Simple program that says bye to NAME for a total of COUNT times."""

    def __call__(self):
        for _ in range(self.count):
            click.echo(f'Bye, {self.name}!')


if __name__ == '__main__':
    # not really instantiating (old) Bye class but calling the new click-wrapping "Bye" function
    Bye()
