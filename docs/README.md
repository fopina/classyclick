# classyclick

`classyclick` lets you define Click commands as classes instead of decorated functions.
It keeps Click's behavior and parameter model, but moves command state onto an
instance so helper methods and properties can use `self` directly.

The documentation is organized with the same split that works well in projects
like Flask: start with the guide if you want to learn the library, then move to
the API reference when you need exact behavior.

## What classyclick provides

- `@classyclick.command()` to turn a class into a `click.Command`
- `classyclick.Option` and `classyclick.Argument` field objects that map class
  attributes to Click parameters
- `classyclick.Context`, `classyclick.ContextObj`, and `classyclick.ContextMeta`
  for injecting Click context values onto the command instance
- `classyclick.Command` and `classyclick.Group` base classes for class-driven
  command and group definitions without an extra decorator

## Installation

```bash
pip install classyclick
```

## A minimal example

```python
import click

import classyclick


@classyclick.command()
class Hello:
    """Simple program that greets NAME for a total of COUNT times."""

    name: str = classyclick.Option(prompt='Your name', help='The person to greet.')
    count: int = classyclick.Option(default=1, help='Number of greetings.')

    def __call__(self):
        for _ in range(self.count):
            click.echo(f'Hello, {self.name}!')


if __name__ == '__main__':
    Hello.click()
```

## Pick a path

- The [Guide](guide.md) explains the main patterns and how the pieces fit
  together.
- The [API Reference](api.md) documents the exported classes, functions, and
  helper utilities module by module.

## Design notes

`classyclick` stays intentionally small. Most keyword arguments and behavior are
forwarded straight to Click, while the library adds a class-centric layer on top:

- field names become parameter names
- type annotations become Click parameter types when possible
- class docstrings become command help text unless you override them
- the generated Click command is attached to the class as `.click`

If you already know Click, you can treat `classyclick` as a thin adapter that
lets you structure larger commands around methods and properties instead of
passing the same values between functions.
