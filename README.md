# $ 🎩click✨_, _classyclick_

[![ci](https://github.com/fopina/classyclick/actions/workflows/publish-main.yml/badge.svg)](https://github.com/fopina/classyclick/actions/workflows/publish-main.yml)
[![test](https://github.com/fopina/classyclick/actions/workflows/test.yml/badge.svg)](https://github.com/fopina/classyclick/actions/workflows/test.yml)
[![codecov](https://codecov.io/github/fopina/classyclick/graph/badge.svg)](https://codecov.io/github/fopina/classyclick)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/classyclick.svg)](https://pypi.org/project/classyclick/)
[![Current version on PyPi](https://img.shields.io/pypi/v/classyclick)](https://pypi.org/project/classyclick/)
[![Very popular](https://img.shields.io/pypi/dm/classyclick)](https://pypistats.org/packages/classyclick)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Class-based definitions of click commands

```
pip install classyclick
```

## A Simple Example

```python
import click
import classyclick


@classyclick.command()
class Hello:
    """Simple program that greets NAME for a total of COUNT times."""

    name: int = classyclick.option(prompt='Your name', help='The person to greet.')
    count: str = classyclick.option(default=1, help='Number of greetings.')

    def __call__(self):
        for _ in range(self.count):
            click.echo(f'Hello, {self.name}!')


if __name__ == '__main__':
    # not really instantiating (old) Hello class but calling the new click-wrapping "Hello" function
    Hello()
```

```
$ python hello.py --count=3
Your name: classyclick
Hello, classyclick!
Hello, classyclick!
Hello, classyclick!
```

## Wait... huh?

_This simple example has even more lines than [click's example](https://github.com/pallets/click/blob/main/README.md#a-simple-example)???_

Right, apart from personal aesthetics preferences, there is no reason to choose class-approach in this example.

Reason why I started to use classes for commands is that, as the command function complexity grows, we decompose it into more functions:

```python
import click

@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    greet(count, name)


def greet(count, name):
    for _ in range(count):
        click.echo(f"Hello, {name}!")
```

See the parameters being passed around?  
Easy to have multiple parameters required to several different functions.

Refactoring to classyclick:

```python
import click
import classyclick


@classyclick.command()
class Hello:
    """Simple program that greets NAME for a total of COUNT times."""

    name: int = classyclick.option(prompt='Your name', help='The person to greet.')
    count: str = classyclick.option(default=1, help='Number of greetings.')

    def __call__(self):
        self.greet()
    
    def greet(self):
        for _ in range(self.count):
            click.echo(f"Hello, {self.name}!")
```

## More

