# Guide

This guide focuses on how `classyclick` is meant to be used in application code.
For exact signatures and lower-level details, see the [API Reference](api.md).

## Define commands with classes

Subclass `classyclick.Command` and implement `__call__()`. The Click command is
built automatically when the class is created:

```python
import click

from classyclick import Command, Option


class Hello(Command):
    name: str = Option(prompt='Your name')

    def __call__(self):
        click.echo(f'Hello, {self.name}!')
```

The generated Click command is available as `Hello.click`.

`classyclick` now only supports class-based declarations. If you are migrating
from the old `@classyclick.command(...)` style, subclass `Command` and move
those keyword arguments into `Command.Config(...)`.

## How fields become Click parameters

`classyclick.Option` and `classyclick.Argument` are dataclass-like field objects.
When the command class is processed:

1. the class is converted to a dataclass
2. each field is read in declaration order
3. each `Option`, `Argument`, or context field wraps the generated Click
   callback

That gives you one place to define the CLI surface and one place to implement
behavior.

### Options

Use `Option` for named parameters:

```python
from pathlib import Path

from classyclick import Command, Option


class Build(Command):
    output: Path = Option(help='Where to write the build output.')
    verbose: bool = Option(help='Enable verbose logging.')
```

Important behaviors:

- the field name is used as the Python parameter name
- `default_parameter=True` adds a long option such as `--output`
- extra positional declarations such as `'-o'` are forwarded to Click
- type annotations are used as the Click `type` when you do not provide one
- `bool` fields become flags by default unless you override `is_flag`

Examples:

```python
count: int = Option(default=1)
count: int = Option('-c', default=1)
count: int = Option('-c', default_parameter=False, default=1)
```

### Arguments

Use `Argument` for positional values:

```python
from classyclick import Argument, Command


class Next(Command):
    your_number: int = Argument()

    def __call__(self):
        print(self.your_number + 1)
```

Important behaviors:

- the argument name always comes from the field name
- the annotation is used as the Click `type` unless you override it
- `Argument` is required by default, matching Click's usual behavior
- if Click determines the argument is optional, the dataclass default is set to
  `None`

### Context injection

Use context fields when the command implementation needs `click.Context` data:

```python
import click

from classyclick import Command, Context, ContextMeta, ContextObj


class ShowState(Command):
    request_id: str = ContextMeta('request_id')
    ctx: click.Context = Context()
    obj: object = ContextObj()

    def __call__(self):
        print(self.ctx.command_path, self.obj, self.request_id)
```

The three context helpers map directly to Click decorators:

- `Context()` behaves like `click.pass_context`
- `ContextObj()` behaves like `click.pass_obj`
- `ContextMeta('key')` behaves like `click.decorators.pass_meta_key`

These values are pushed into the generated callback and then copied into the
class instance before `__call__()` runs.

## Names, help text, and Click kwargs

By default, `classyclick` derives the Click callback name from the class name:

- class name `HelloWorld` becomes callback name `hello_world`
- Click then applies its normal command-name conversion, typically resulting in
  `hello-world`

The class docstring becomes the command help text unless you provide `help=`
explicitly.

You can pass normal Click configuration on `Command.Config`:

```python
from classyclick import Command


class Hello(Command):
    __config__ = Command.Config(name='hello-there', help='Friendly greeting command.')
```

`Command.Config` also accepts `group=` so a command can register itself under a
specific Click group.

It also accepts `decorators=` for additional Click decorators such as
`click.version_option(...)`.

## Working with groups

For grouped CLIs, subclass `classyclick.Group`:

```python
import click

from classyclick import Group, Option


class CLI(Group):
    debug: bool = Option(default=False)

    def __call__(self):
        click.echo(f'debug={self.debug}')


class Hello(CLI.Command):
    name: str = Option(prompt='Your name')

    def __call__(self):
        click.echo(f'Hello, {self.name}!')
```

When a `Group` subclass is created, `classyclick`:

- builds a `click.Group` and stores it as `.click`
- creates `Group.Command` and `Group.SubGroup` helper base classes
- also exposes `Group.CommandMixin` and `Group.SubGroupMixin` for cases where
  you need to combine the group binding with your own command/group base class
- binds those helper bases so child commands and sub-groups register beneath the
  parent group automatically

This gives you a compact way to build nested CLIs while keeping each command as
its own class.

## Helper utilities

`classyclick.helpers` contains optional building blocks for larger CLIs.

### Auto-discover command modules

When a CLI is split across many modules, importing those modules is often enough
to register their `Group.Command` and `Group.SubGroup` subclasses.

`classyclick.helpers.discover_commands()` automates that import step:

```python
import classyclick


class CLI(classyclick.Group):
    """Application CLI."""


classyclick.helpers.discover_commands(__package__)
```

This walks the package recursively and imports each module once.

### Config-backed CLIs

`classyclick.helpers.ConfigFileMixin` lets a command or group load defaults from
`config.toml`.

A common pattern is:

```python
from pathlib import Path

import click

import classyclick


class CLI(classyclick.helpers.ConfigFileMixin, classyclick.Group):
    """Application CLI."""

    __config__ = classyclick.Group.Config(
        context_settings=dict(show_default=True),
        decorators=[click.version_option(version='1.2.3', message='%(version)s')],
    )
    CONFIG_DEFAULT_NAME = 'my-app'
    CONFIG_EXAMPLE_PATH = Path(__file__).parent / 'config.example.toml'

    host: str = classyclick.Option(help='Server URL')
    token: str = classyclick.Option(help='API token')
    debug: bool = classyclick.Option(help='Enable debug logging')

    def __call__(self):
        self.load_config()


class Config(classyclick.helpers.ConfigBaseCommand, CLI.Command):
    """Show or edit the current CLI configuration."""


classyclick.helpers.discover_commands(__package__)
```

The mixin adds `--config` and `--env` options and a `ctx` field automatically.
Call `self.load_config()` before you use config-backed values.

`ConfigBaseCommand` is an optional helper command that prints the merged config
or opens the file in `$VISUAL` / `$EDITOR`.

### `config.toml` behavior

The config file is intentionally aligned with the CLI:

- root-level keys act as defaults for matching `classyclick` fields
- command-line flags still win over config values
- `--config` only selects which file to read, so it is not itself stored inside
  `config.toml`
- `--env` selects an `[env.<name>]` section, while `default_env` provides the
  default environment value

Example:

```toml
default_env = "dev"
host = "https://api.example.com"

[env.dev]
token = "dev-token"
debug = true

[env.prod]
token = "prod-token"
```

With this file:

- `my-app status` uses the `dev` environment because of `default_env`
- `my-app --env prod status` merges `[env.prod]` over the root config
- `my-app --env prod --host https://staging.example.com status` still uses the
  `prod` config, but the CLI flag overrides `host`

## Required field ordering

Because command classes are converted to dataclasses, dataclass ordering rules
still apply:

- required fields must come before optional fields
- this matters for `Argument`, `Option(required=True)`, and `ContextMeta`
- optional context values such as `Context` and `ContextObj` should be declared
  after required fields

If a class contains a `classyclick` field without a type annotation,
`strictly_typed_dataclass()` raises a `TypeError`.
