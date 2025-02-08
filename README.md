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


@click.option('--name', prompt='Your name', help='The person to greet.')
@click.option('--count', default=1, help='Number of greetings.')
@classyclick.command()
class Hello:
    """Simple program that greets NAME for a total of COUNT times."""

    count: int
    name: str

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

## Usage

```python
>>> from example import demo
>>> demo.echo('ehlo')
'EHLO right back at ya!'
```

## Build

Check out [CONTRIBUTING.md](CONTRIBUTING.md)
