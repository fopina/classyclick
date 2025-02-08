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
    """Simple program that greets reversed NAME for a total of COUNT times."""
    greet(count, name)


def greet(count, name):
    for _ in range(count):
        click.echo(f"Hello, {reverse(name)}!")

def reverse(name):
    return name[::-1]
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
            click.echo(f"Hello, {self.reversed_name}!")
    
    @property
    def reversed_name(self):
        return self.name[::-1]
```

## More docs please

Not much to add to the simple example currently, as this mostly forwards everything to click, but here's something more then!

### classyclick.command

Use it just like [@click.command](https://click.palletsprojects.com/en/stable/api/#click.command) but decorating a **class** instead of a function (*classy*).

The only new keyword argument is `group`. This can be used to attach the command a `click.group`.

Re-using click examples:

```
@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}")

@cli.command()  # @cli, not @click!
def sync():
    click.echo('Syncing')

@classyclick.command(group=cli)  # classy! with group
class AnotherSync:
    ...
```

Same as `click.command`, you can choose a command `name` or allow it to derive it from class name (camel to kebab, instead of click's snake to kebab).

It will also forward class `__doc__` to click to be used as description if not specified as keyword arg.

### classyclick.option

Instead of the decorator approach, this is more like [Django's models](https://docs.djangoproject.com/en/dev/topics/db/models/) to take advantage of how parameters are enumerated.

As you noticed from the example, there's no need to specify an option parameter name:

```
count: str = classyclick.option(default=1, help='Number of greetings.')
```

`classyclick` makes use of the field names to infer a default (`--count` in example).

To add a short version *on top of it*:

```
count: str = classyclick.option('-c', default=1, help='Number of greetings.')
```

And to only include the short, you can use the only keyword argument that is not forwarded to `click.option`: `default_parameter`

```
count: str = classyclick.option('-c', default_parameter=False, default=1, help='Number of greetings.')
```

### Testing

`classyclick` is just a small wrapper around `click`, testing is the same as in [click's docs](https://click.palletsprojects.com/en/stable/testing/#basic-testing):

```python
from click.testing import CliRunner
# Hello being the example above that reverses name
# notice that the wrapped `click.command` gets the same casing as the class
from hello import Hello

def test_hello_world():
  runner = CliRunner()
  result = runner.invoke(Hello, ['--name', 'Peter'])
  assert result.exit_code == 0
  assert result.output == 'Hello reteP!\n'
```

Not very common or documented, but, in `click`, you could use the `click.command` `callback` parameter to call the unwrapped function.  

This was not very useful (as you'd have to capture output yourself, etc) but it might be more interesting with classes, as you might want to unit test specific methods in the class.

`Hello.callback` (from the example) will point to an anonymous function that wraps the class - use `Hello.callback._classy_` instead!

This might help reducing required test setup as you don't need to control complex code paths from entrypoint of the CLI command:

```python
# notice that the wrapped `click.command` gets the same casing as the class
from hello import Hello

def test_hello_world():
  # for the example above that reverses the name
  o = Hello.callback._classy_('hello', 1)
  assert o.reversed_name == 'olleh'
```
