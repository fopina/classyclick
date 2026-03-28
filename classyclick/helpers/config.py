"""Configuration inspection and editing command."""

import json
import os
import shlex
import shutil
import subprocess

import click

import classyclick

_MASKED = '<masked>'
_SECRET_FIELD_PARTS = ('token', 'password')


def _mask_value(key: str, value):
    if isinstance(value, dict):
        return {nested_key: _mask_value(nested_key, nested_value) for nested_key, nested_value in value.items()}

    if isinstance(value, list):
        return [_mask_value(key, item) for item in value]

    if value is None:
        return None

    if any(part in key.lower() for part in _SECRET_FIELD_PARTS):
        return _MASKED

    return value


def _resolve_editor() -> str:
    editor = os.environ.get('VISUAL') or os.environ.get('EDITOR')
    if editor:
        return editor

    for fallback in ('vim', 'vi', 'nano'):
        if shutil.which(fallback):
            return fallback

    raise click.ClickException('No editor configured. Set VISUAL or EDITOR, or install vim, vi, or nano.')


class ConfigBaseCommand(classyclick.Command):
    """Show or edit the current CLI configuration"""

    edit: bool = classyclick.Option('-e', help='Open the config file in $VISUAL or $EDITOR')
    ctx: click.Context = classyclick.Context()

    def __call__(self):
        config_path = self.ctx.meta['config_path']

        if self.edit:
            editor = _resolve_editor()
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

        click.echo(json.dumps(_mask_value('config', config), indent=2, sort_keys=True))
