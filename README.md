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

    name: str = classyclick.option(prompt='Your name', help='The person to greet.')
    count: int = classyclick.option(default=1, help='Number of greetings.')

    def __call__(self):
        for _ in range(self.count):
            click.echo(f'Hello, {self.name}!')


if __name__ == '__main__':
    Hello.click()
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

    name: str = classyclick.option(prompt='Your name', help='The person to greet.')
    count: int = classyclick.option(default=1, help='Number of greetings.')

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
count: int = classyclick.option(default=1, help='Number of greetings.')
```

`classyclick` makes use of the field names to infer a default (`--count` in example).

To add a short version *on top of it*:

```
count: int = classyclick.option('-c', default=1, help='Number of greetings.')
```

And to only include the short, you can use the only keyword argument that is not forwarded to [@click.option](https://click.palletsprojects.com/en/stable/api/#click.option): `default_parameter`

```
count: int = classyclick.option('-c', default_parameter=False, default=1, help='Number of greetings.')
```

`classyclick.option` also infers **type** from type hints, then passed to `click.option`.

```python
# The resulting click.option will use type=Path
output: Path = classyclick.option()

# You can still override it and mix things if you want ¯\_(ツ)_/¯
other_output: Any = classyclick.option(type=str)
```

When type is `bool`, it will set `is_flag=True` as well. If for some reason you don't want that, it can still be overriden.

```python
# This results in click.option('--verbose', type=bool, is_flag=True)
verbose: bool = classyclick.option()

# As mentioned, it can always be overriden if you need the weird behavior of a non-flag bool option...
weird: bool = classyclick.option(is_flag=False)
```

### classyclick.argument

Similar to `classyclick.option`, this is mostly wrapping [@click.argument](https://click.palletsprojects.com/en/stable/api/#click.argument) so it can be used in fields.

Argument name is inferred from the field name and, same as `classyclick.option`, type from field.type.  
Again, type can be overriden, however not argument name as it has to match the property. For display purposes, you can use `metavar=`.

```python
@classyclick.command()
class Next:
    """Output the next number."""

    your_number: int = classyclick.argument()

    def __call__(self):
        click.echo(self.your_number + 1)
```

```
$ ./cli_four.py --help
Usage: cli_four.py [OPTIONS] YOUR_NUMBER

  Output the next number.

Options:
  --help  Show this message and exit.

$ ./cli_four.py 5     
6
```

### classyclick.context

Like [@click.pass_context](https://click.palletsprojects.com/en/stable/api/#click.pass_context), this exposes `click.Context` in a command property.

```python
@classyclick.command()
class Next:
    """Output the next number."""

    your_number: int = classyclick.argument()
    the_context: Any = classyclick.context()

    def __call__(self):
        click.echo(self.your_number + self.the_context.obj.step_number)
```

### classyclick.context_obj

Like [@click.pass_obj](https://click.palletsprojects.com/en/stable/api/#click.pass_obj), this assigns `click.Context.obj` to a command property, when you only want the user data rather than the whole context.

```python
@classyclick.command()
class Next:
    """Output the next number."""

    your_number: int = classyclick.argument()
    the_context: Any = classyclick.context_obj()

    def __call__(self):
        click.echo(self.your_number + self.the_context.step_number)
```

### classyclick.context_meta

Like [@click.pass_meta_key](https://click.palletsprojects.com/en/stable/api/#click.decorators.pass_meta_key), this assigns `click.Context.meta[KEY]` to a command property, without handling the whole context.

```python
@classyclick.command()
class Next:
    """Output the next number."""

    your_number: int = classyclick.argument()
    step_number: int = classyclick.context_meta("step_number")

    def __call__(self):
        click.echo(self.your_number + self.step_number)
```

### Composition

You can compose commands together as the wrapped class is just a `dataclass`.

As example, if we wanted a `Bye` command just like the `Hello` example above, but with a small change, we can subclass `Hello`

```python
import click
import classyclick


@classyclick.command()
class Bye(Hello):
    """Simple program that says bye to NAME for a total of COUNT times."""

    def greet(self):
        for _ in range(self.count):
            click.echo(f"Bye, {self.reversed_name}!")
```

The command is subclassed, inheriting arguments/options (as they are dataclass fields) and any methods:

```
$ ./bye.py --help

Usage: bye.py [OPTIONS]

  Simple program that says bye to NAME for a total of COUNT times.

Options:
  --name TEXT          The person to greet.
  -c, --count INTEGER  Number of greetings.
  --help               Show this message and exit.
```

### Testing

`classyclick` is just a small wrapper around `click`, testing is the same as in [click's docs](https://click.palletsprojects.com/en/stable/testing/#basic-testing):

Simply use `Command.click` with `CliRunner` for the same `click.testing` experience

```python
from click.testing import CliRunner
# Hello being the example above that reverses name
from hello import Hello

def test_hello_world():
  runner = CliRunner()
  result = runner.invoke(Hello.click, ['--name', 'Peter'])
  assert result.exit_code == 0
  assert result.output == 'Hello reteP!\n'
```

But you can also unit test specific methods of a command, skipping `CliRunner`.

This might help reducing required test setup as you don't need to control complex code paths from entrypoint of the CLI command.

```python
from hello import Hello

def test_hello_world():
# for the example above that reverses the name
o = Hello('hello', 1)
assert o.reversed_name == 'olleh'
```