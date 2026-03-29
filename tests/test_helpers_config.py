from pathlib import Path
from tempfile import TemporaryDirectory

import click

import classyclick
from classyclick.helpers.config import ConfigBaseCommand, ConfigFileMixin, merge_dicts
from tests import BaseCase


class TestConfigBaseCommand(BaseCase):
    def test_mask_value_uses_class_configuration(self):
        class CustomConfigCommand(ConfigBaseCommand):
            __classyclick_skip_build__ = True
            MASKED = '[redacted]'
            MASKED_FIELDS = ('user_secret', 'client_secret', 'api_secret')

        masked = CustomConfigCommand._mask_value(
            'config',
            {
                'api_secret': 'abc123',
                'api_token': 'still-visible',
                'nested': {
                    'user_secret': 'def456',
                    'password': 'still-visible',
                },
                'items': [
                    {
                        'client_secret': 'ghi789',
                        'token': 'still-visible',
                    }
                ],
            },
        )

        self.assertEqual(
            masked,
            {
                'api_secret': '[redacted]',
                'api_token': 'still-visible',
                'nested': {
                    'user_secret': '[redacted]',
                    'password': 'still-visible',
                },
                'items': [
                    {
                        'client_secret': '[redacted]',
                        'token': 'still-visible',
                    }
                ],
            },
        )

    def test_resolve_editor_uses_class_override(self):
        class CustomConfigCommand(ConfigBaseCommand):
            __classyclick_skip_build__ = True

            @classmethod
            def _resolve_editor(cls):
                return 'custom-editor --flag'

        self.assertEqual(CustomConfigCommand._resolve_editor(), 'custom-editor --flag')


class TestConfigFileMixin(BaseCase):
    def test_merge_dicts_merges_nested_values(self):
        self.assertEqual(
            merge_dicts(
                {'token': 'root', 'nested': {'enabled': True, 'timeout': 10}},
                {'nested': {'timeout': 20}, 'retries': 3},
            ),
            {'token': 'root', 'nested': {'enabled': True, 'timeout': 20}, 'retries': 3},
        )

    def test_ensure_config_file_uses_class_default_path(self):
        with TemporaryDirectory() as tmpdir:
            default_path = Path(tmpdir) / 'custom.toml'

            class CustomConfigMixin(ConfigFileMixin):
                DEFAULT_PATH = default_path
                EXAMPLE_PATH = None

            self.assertEqual(CustomConfigMixin.ensure_config_file(None), default_path)
            self.assertFalse(default_path.exists())

    def test_ensure_config_file_copies_example_only_when_configured(self):
        with TemporaryDirectory() as tmpdir:
            default_path = Path(tmpdir) / 'config.toml'
            example_path = Path(tmpdir) / 'config.example.toml'
            example_path.write_text('name = "demo"\n')

            class CustomConfigMixin(ConfigFileMixin):
                DEFAULT_PATH = default_path
                EXAMPLE_PATH = example_path

            self.assertEqual(CustomConfigMixin.ensure_config_file(None), default_path)
            self.assertEqual(default_path.read_text(), 'name = "demo"\n')

    def test_load_config_uses_overridable_class_methods(self):
        calls = []

        class CustomConfigMixin(ConfigFileMixin):
            @classmethod
            def ensure_config_file(cls, config_path):
                calls.append(('ensure', config_path))
                return Path('/tmp/custom-config.toml')

            @classmethod
            def load_config_data(cls, config_path):
                calls.append(('load', config_path))
                return {'default_env': None}

        command = CustomConfigMixin.__new__(CustomConfigMixin)
        command.config = None
        command.env = None

        command.load_config()

        self.assertEqual(
            calls,
            [
                ('ensure', None),
                ('load', Path('/tmp/custom-config.toml')),
            ],
        )
        self.assertEqual(command.config, Path('/tmp/custom-config.toml'))

    def test_load_config_populates_unset_classyclick_fields_from_config(self):
        class CustomConfigMixin(ConfigFileMixin):
            token: str = classyclick.Option(default='default-token')
            username: str = classyclick.Option()
            enabled: bool = classyclick.Option(default=False)
            retries: int = classyclick.Option(default=3)

            @classmethod
            def ensure_config_file(cls, config_path):
                return Path('/tmp/custom-config.toml')

            @classmethod
            def load_config_data(cls, config_path):
                return {
                    'default_env': None,
                    'token': 'config-token',
                    'username': 'config-user',
                    'enabled': True,
                    'retries': 8,
                }

        command = CustomConfigMixin.__new__(CustomConfigMixin)
        command.config = None
        command.env = None
        command.token = 'default-token'
        command.username = None
        command.enabled = False
        command.retries = 7

        command.load_config()

        self.assertEqual(command.token, 'config-token')
        self.assertEqual(command.username, 'config-user')
        self.assertTrue(command.enabled)
        self.assertEqual(command.retries, 7)

    def test_subclass_default_path_updates_click_show_default(self):
        class CustomConfigCommand(ConfigFileMixin, classyclick.Command):
            DEFAULT_PATH = Path('/tmp/custom-config.toml')
            EXAMPLE_PATH = None
            ctx: click.Context = classyclick.Context()

            def __call__(self):
                return None

        config_param = next(param for param in CustomConfigCommand.click.params if param.name == 'config')
        self.assertEqual(config_param.show_default, str(Path('/tmp/custom-config.toml')))
