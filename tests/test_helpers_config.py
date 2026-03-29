from classyclick.helpers.config import ConfigBaseCommand
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
