# API Reference

This reference follows the package layout in `classyclick/` and documents the
library's public API first, then the internal helpers that appear in the source.

## Package exports

The top-level `classyclick` package re-exports the main public API from
`classyclick.__init__`:

- `__version__`, `version`
- `Command`
- `Group`
- `Option`, `Argument`, `Context`, `ContextObj`, `ContextMeta`
- `command`
- `option`, `argument`, `context`, `context_obj`, `context_meta`

Importing from the package root is the intended user-facing style.

## `classyclick.__version__`

### `version` and `__version__`

String aliases for the installed package version.

### `version_tuple` and `__version_tuple__`

Tuple forms derived from `version.split('.')`. These exist in the module, but
only the string versions are exported through `__all__`.

## `classyclick.command`

### `Command`

Base class for defining commands.

Key behavior:

- subclasses must implement `__call__()`
- subclasses are converted to dataclasses automatically
- the Click command is built in `__init_subclass__`
- the generated command is stored as `Class.click`

This is the most direct choice when you want a class-first API.

### `Command.click`

Class attribute containing the generated `click.Command`.

### `Command.__config__`

Optional class attribute. Set this to a `Command.Config` instance to pass named
configuration into Click command creation.

### `Command.Config`

Configuration container for `Command`.

Constructor parameters:

- `name`: override the generated command name
- `help`: override the help text that would otherwise come from the class
  docstring
- `group`: register the command under a specific Click group
- `**kwargs`: forwarded to `click.command()`

### `Command.__init_subclass__(**kwargs)`

Called automatically when a subclass is declared.

It enforces that concrete command subclasses implement `__call__()` unless they
opt out with `__classyclick_skip_build__`, then builds the Click command.

### `Command._build_click_command()`

Class method that delegates to the shared group/command builder in
`classyclick.group`.

This is effectively an internal extension point.

### `command(cls=None, *, group=None, **click_kwargs)`

Compatibility decorator that turns a class into a Click command.

It follows the same build path as `Command`, including dataclass conversion,
field processing, callback creation, and storing the generated Click command on
the class as `.click`.

Prefer subclassing `Command` in new code. This decorator remains useful when
you need to adapt an existing plain class without changing its base class.

### `Clickable`

`typing.Protocol` used for type hints. It describes an object with a `.click`
attribute containing the generated `click.Command`.

This is not a runtime feature; it exists to help type checkers understand what
the decorator returns.

## `classyclick.fields`

### `Option(*param_decls, default_parameter=True, **attrs)`

Field object that maps a class attribute to `click.option()`.

Special behavior added by `classyclick`:

- prepends the field name as the Click parameter name
- adds a default long option such as `--dry-run` when
  `default_parameter=True`
- infers `type` from the field annotation when `type` is omitted
- converts `bool` annotations into flags unless `is_flag` is already set
- mirrors Click's required/default handling back onto the dataclass field

Rules and caveats:

- positional `param_decls` must start with `-`; the field name already supplies
  the destination name
- `required=True` makes the field a required dataclass field
- declaration order still matters because the owning class becomes a dataclass

### `Option.__call__(command)`

Applies the stored option definition to a Click callback and returns the wrapped
callback.

### `Argument(*, type=None, **attrs)`

Field object that maps a class attribute to `click.argument()`.

Special behavior added by `classyclick`:

- the argument name always comes from the field name
- the annotation is used as `type` unless you provide one
- required/optional status is mirrored back into the dataclass field default

Because it represents a positional value, there is no equivalent to
`default_parameter`.

### `Argument.__call__(command)`

Applies the argument definition to a Click callback.

### `Context()`

Field object that injects `click.Context`, similar to `click.pass_context`.

Behavior:

- stores the field name on a private `__classy_context__` list on the callback
- wraps the callback with `click.pass_context`
- defaults to `None` on the dataclass side so the field is optional

### `ContextObj()`

Like `Context()`, but injects `click.Context.obj` using `click.pass_obj`.

### `ContextMeta(key, **attrs)`

Injects `click.Context.meta[key]` using `click.decorators.pass_meta_key`.

Unlike `Context` and `ContextObj`, this is required by default because Click
raises `KeyError` when the key is missing.

### Lowercase helper functions

These helpers create the corresponding field objects and are kept for
compatibility:

- `option(*param_decls, default_parameter=True, **attrs)` -> `Option`
- `argument(*, type=None, **attrs)` -> `Argument`
- `context()` -> `Context`
- `context_obj()` -> `ContextObj`
- `context_meta(key, **attrs)` -> `ContextMeta`

Prefer the capitalized class names in new code.

### `_Field`

Internal base class shared by all field types.

It subclasses `dataclasses.Field`, stores Click attributes, infers types from
annotations, and performs the trick that keeps Click's required/default behavior
aligned with dataclass field defaults.

This class is part of the implementation, not the supported public API.

### `_FakeCommand`

Internal helper used during field setup to let Click build a parameter object so
`classyclick` can inspect the resulting default and required state.

Application code should not use this directly.

## `classyclick.group`

### `Group`

Base class for defining `click.Group` objects as classes.

Like `Command`, it auto-builds the Click object during subclass creation, but it
also wires helper base classes for nested commands.

### `Group.click`

Class attribute containing the generated `click.Group`.

### `Group.__config__`

Optional class attribute. Set this to `Group.Config(...)` to customize how the
Click group is created.

### `Group.Config`

Configuration container for groups.

Constructor parameters:

- `name`: override the generated group name
- `help`: override the group help text
- `**kwargs`: forwarded to `click.group()`

### `Group.__init_subclass__(**kwargs)`

Builds the Click group for each concrete subclass and then binds helper base
classes for nested commands and sub-groups.

### `Group._build_click_group()`

Class method that delegates to the shared command/group builder.

### `Group._bind_children()`

Creates and attaches four helper classes:

- `Group.CommandMixin`
- `Group.SubGroupMixin`
- `Group.Command`
- `Group.SubGroup`

These helper bases carry the parent group configuration so child command classes
register themselves beneath the group automatically.

### `Group.__call__()`

Placeholder implementation so groups do not need to define a body unless they
want startup behavior of their own.

### `_build_click_class_command(cls, *, is_group=False)`

Internal shared builder used by both `Command` and `Group`.

It:

- converts the class into a dataclass
- creates the wrapper callback
- applies all field objects
- merges configuration from `__config__` and `__click_*__` class attributes
- resolves parent-group registration rules
- registers either a `click.Command` or `click.Group`

### `_get_base_group_config(cls)`

Internal helper that walks the class MRO looking for inherited group-binding
configuration.

## `classyclick.utils`

### `camel_kebab(camel_value)`

Converts `CamelCase` into `camel-case`.

### `camel_snake(camel_value)`

Converts `CamelCase` into `camel_case`.

This is used when generating the intermediate callback name before Click applies
its own command-name normalization.

### `snake_kebab(snake_value)`

Converts `snake_case` into `snake-case`.

This is used for auto-generated option names such as `--dry-run`.

### `strictly_typed_dataclass(kls)`

Wraps `dataclasses.dataclass()` but first checks that every `classyclick` field
has a type annotation.

If a field object such as `Option()` or `Argument()` appears without a matching
annotation, it raises `TypeError`.

This function is a core internal guardrail and can also be useful when reading
stack traces from invalid command declarations.
