#!/usr/bin/env python3
# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
# README +++
import click

import classyclick


class Hello(classyclick.Command):
    """Simple program that greets reversed NAME for a total of COUNT times."""

    name: str = classyclick.Option(prompt='Your name', help='The person to greet.')
    count: int = classyclick.Option(default=1, help='Number of greetings.')

    def __call__(self):
        self.greet()

    def greet(self):
        for _ in range(self.count):
            click.echo(f'Hello, {self.reversed_name}!')

    @property
    def reversed_name(self):
        return self.name[::-1]


# README ---


class PlainHello(classyclick.Command):
    """Simple program that greets NAME for a total of COUNT times."""

    name: str = classyclick.Option(prompt='Your name', help='The person to greet.')
    count: int = classyclick.Option('-c', default=1, help='Number of greetings.')

    def __call__(self):
        for _ in range(self.count):
            click.echo(f'Hello, {self.name}!')


if __name__ == '__main__':
    PlainHello.click()
