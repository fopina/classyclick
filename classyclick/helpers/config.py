"""Configuration inspection and editing command."""

import json
import os
import shlex
import shutil
import subprocess
from dataclasses import MISSING, dataclass, fields
from pathlib import Path
from typing import Optional

import click
from platformdirs import user_config_dir

import classyclick
from classyclick.fields import _Field

try:
    # Python 3.11+
    import tomllib
except ModuleNotFoundError:
    # Python < 3.11
    import tomli as tomllib  # type: ignore


def merge_dicts(base: dict, override: dict) -> dict:
    """
    To merge two Python dictionaries where:
    * nested dictionaries should merge recursively
    * lists and other values should be replaced entirely

    by ChatGPT
    """
    result = base.copy()
    for key, value in override.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value
        else:
            result[key] = value
    return result


@dataclass
class ConfigFileMixin:
    CONFIG_DEFAULT_NAME = None
    CONFIG_DEFAULT_PATH = Path(user_config_dir(CONFIG_DEFAULT_NAME)) / 'config.toml'
    CONFIG_EXAMPLE_PATH = None

    # do not set default now
    config: Path = classyclick.Option(help='Path to the configuration file')
    env: str = classyclick.Option(
        '-e', help='Environment to use for the command (as many can be specified in config.toml)'
    )
    ctx: classyclick.Context = classyclick.Context()

    def __init_subclass__(cls):
        if cls.CONFIG_DEFAULT_PATH == ConfigFileMixin.CONFIG_DEFAULT_PATH:
            if cls.CONFIG_DEFAULT_NAME is None:
                cls.CONFIG_DEFAULT_NAME = cls.__module__.split('.')[0]
            cls.CONFIG_DEFAULT_PATH = Path(user_config_dir(cls.CONFIG_DEFAULT_NAME)) / 'config.toml'
        # override show_default now we all re-calculated
        cls.__dataclass_fields__['config'].attrs['show_default'] = str(cls.CONFIG_DEFAULT_PATH)

        if cls.CONFIG_EXAMPLE_PATH is None:
            raise ValueError(
                'CONFIG_EXAMPLE_PATH is not defined. It is strongly recommended to include an example config.toml in your package. If you do not want to include one, set this attribute to False'
            )
        if cls.CONFIG_EXAMPLE_PATH is not False:
            if not isinstance(cls.CONFIG_EXAMPLE_PATH, Path):
                raise ValueError('CONFIG_EXAMPLE_PATH must be of type Path')
            if not cls.CONFIG_EXAMPLE_PATH.exists():
                raise ValueError(f'CONFIG_EXAMPLE_PATH path {cls.CONFIG_EXAMPLE_PATH} does not exist')
        super().__init_subclass__()

    @classmethod
    def ensure_config_file(cls, config_path: Optional[Path]) -> Path:
        config_path = config_path or cls.CONFIG_DEFAULT_PATH
        if not config_path.exists() and cls.CONFIG_EXAMPLE_PATH is not None:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(Path(cls.CONFIG_EXAMPLE_PATH).read_text())
            print(f'Info: No configuration file found at {config_path}, a sample config has been placed there.')

        return config_path

    @classmethod
    def load_config_data(cls, config_path: Path) -> dict:
        with config_path.open('rb') as f:
            return tomllib.load(f)

    def load_config(self):
        self.config = type(self).ensure_config_file(self.config)
        config_data = type(self).load_config_data(self.config)

        if self.env is None:
            self.env = config_data.get('default_env')

        # allow empty string to choose root environment when "default_env" is set to something else
        if self.env:
            if self.env not in config_data.get('env', {}):
                raise click.ClickException(f'Environment "{self.env}" not found in {self.config}')
            env_config = config_data['env'][self.env]
            config_data = merge_dicts(config_data, env_config)

        ignored_fields = {field.name for field in fields(ConfigFileMixin)}
        for field in fields(self):
            if field.name in ignored_fields:
                # these are not sourced from config - and env is matched with default_env above
                continue

            if not isinstance(field, _Field) or field.name not in config_data:
                continue

            current_value = getattr(self, field.name, MISSING)
            default_value = field.default
            if current_value is None or (default_value is not MISSING and current_value == default_value):
                setattr(self, field.name, config_data[field.name])

        self.ctx.meta['config_path'] = self.config
        self.ctx.meta['config_data'] = config_data
        self.ctx.meta['selected_env'] = self.env
        self.ctx.default_map = config_data


class ConfigBaseCommand(classyclick.Command):
    """Show or edit the current CLI configuration"""

    MASKED = '<masked>'
    MASKED_FIELDS = ('token', 'password')

    edit: bool = classyclick.Option('-e', help='Open the config file in $VISUAL or $EDITOR')
    ctx: click.Context = classyclick.Context()

    @classmethod
    def _mask_value(cls, key: str, value):
        if isinstance(value, dict):
            return {nested_key: cls._mask_value(nested_key, nested_value) for nested_key, nested_value in value.items()}

        if isinstance(value, list):
            return [cls._mask_value(key, item) for item in value]

        if value is None:
            return None

        if any(key.lower() == field.lower() for field in cls.MASKED_FIELDS):
            return cls.MASKED

        return value

    @classmethod
    def _resolve_editor(cls) -> str:
        editor = os.environ.get('VISUAL') or os.environ.get('EDITOR')
        if editor:
            return editor

        for fallback in ('vim', 'vi', 'nano'):
            if shutil.which(fallback):
                return fallback

        raise click.ClickException('No editor configured. Set VISUAL or EDITOR, or install vim, vi, or nano.')

    def __call__(self):
        config_path = self.ctx.meta['config_path']

        if self.edit:
            editor = self._resolve_editor()
            try:
                subprocess.run([*shlex.split(editor), str(config_path)], check=True)
            except FileNotFoundError as exc:
                raise click.ClickException(f'Editor command not found: {editor}') from exc
            except subprocess.CalledProcessError as exc:
                raise click.ClickException(f'Editor exited with status {exc.returncode}') from exc
            return

        config = {key: value for key, value in self.ctx.meta['config_data'].items() if key != 'env'}

        click.echo(f'Config file: {click.style(str(config_path), bold=True)}')
        if self.ctx.meta['selected_env']:
            click.echo(f'Environment: {click.style(self.ctx.meta["selected_env"], bold=True)}')

        click.echo(json.dumps(self._mask_value('config', config), indent=2, sort_keys=True))
