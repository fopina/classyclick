# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import click

import classyclick
from tests.cli_one import Hello


@classyclick.command()
class Bye(Hello):
    """Simple program that says bye to NAME for a total of COUNT times."""

    def __call__(self):
        for _ in range(self.count):
            click.echo(f'Bye, {self.name}!')


if __name__ == '__main__':
    Bye.click()
