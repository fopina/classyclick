#!/usr/bin/env python3
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
    # README:normal +++
    count: int = classyclick.Option(default=1, help='Number of greetings.')
    # README:normal ---
    # README:short +++
    count: int = classyclick.Option('-c', default=1, help='Number of greetings.')
    # README:short ---
    # README:defaultparam +++
    count: int = classyclick.Option('-c', default_parameter=False, default=1, help='Number of greetings.')
    # README:defaultparam ---
    # README:bool +++
    # This results in click.option('--verbose', type=bool, is_flag=True)
    verbose: bool = classyclick.Option()

    # As mentioned, it can always be overriden if you need the weird behavior of a non-flag bool option...
    weird: bool = classyclick.Option(is_flag=False)
    # README:bool ---
    # README:type +++
    # The resulting click.option will use type=Path
    output: Path = classyclick.Option()

    # You can still override it and mix things if you want ¯\_(ツ)_/¯
    other_output: any = classyclick.Option(type=str)
    # README:type ---

    def __call__(self):
        self.greet()

    def greet(self):
        for _ in range(self.count):
            click.echo(f'Hello, {self.reversed_name}!')

    @property
    def reversed_name(self):
        return self.name[::-1]


if __name__ == '__main__':
    Hello.click()
