# sys.path tampering only to use dev classyclick - not usually required!
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import click

import classyclick


@classyclick.command()
class Hello:
    """Simple program that greets NAME for a total of COUNT times."""

    count: int = classyclick.option('--name', prompt='Your name', help='The person to greet.')
    name: str = classyclick.option('--count', default=1, help='Number of greetings.')

    not_an_option: str = 'test'

    def __call__(self):
        for _ in range(self.count):
            click.echo(f'Hello, {self.name}!')


if __name__ == '__main__':
    # not really instantiating (old) Hello class but calling the new click-wrapping "Hello" function
    Hello()
