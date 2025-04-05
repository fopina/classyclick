from classyclick import utils
from tests import BaseCase


class Test(BaseCase):
    def test_camel_kebab(self):
        self.assertEqual(utils.camel_kebab('CamelCase'), 'camel-case')
        self.assertEqual(utils.camel_kebab('Case'), 'case')
        self.assertEqual(utils.camel_kebab('Camel123Case'), 'camel123-case')

    def test_snake_kebab(self):
        self.assertEqual(utils.snake_kebab('dry_run'), 'dry-run')
