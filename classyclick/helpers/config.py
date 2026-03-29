"""Configuration inspection and editing command."""

import json
import os
import shlex
import shutil
import subprocess

import click

import classyclick


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
