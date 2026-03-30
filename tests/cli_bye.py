#!/usr/bin/env python3
# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

# README +++
import click
from cli_hello import Hello

import classyclick


class Bye(Hello):
    """Simple program that says bye to NAME for a total of COUNT times."""

    def greet(self):
        for _ in range(self.count):
            click.echo(f'Bye, {self.reversed_name}!')


# README ---


@classyclick.command()
class Bye(Hello):
    """Simple program that says bye to NAME for a total of COUNT times."""

    count: int = classyclick.Option(default=1, help='Number of greetings.')

    def __call__(self):
        for _ in range(self.count):
            click.echo(f'Bye, {self.name}!')


if __name__ == '__main__':
    Bye.click()
