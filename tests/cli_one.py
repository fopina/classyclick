# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import click

import classyclick


@classyclick.command()
class Hello:
    """Simple program that greets NAME for a total of COUNT times."""

    name: str = classyclick.Option(prompt='Your name', help='The person to greet.')
    count: int = classyclick.option('-c', default=1, help='Number of greetings.')

    def __call__(self):
        for _ in range(self.count):
            click.echo(f'Hello, {self.name}!')


if __name__ == '__main__':
    Hello.click()
