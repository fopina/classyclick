from unittest import TestCase

from classyclick import utils


class Test(TestCase):
    def test_camel_kebab(self):
        self.assertEqual(utils.camel_kebab('CamelCase'), 'camel-case')
        self.assertEqual(utils.camel_kebab('Case'), 'case')
        self.assertEqual(utils.camel_kebab('Camel123Case'), 'camel123-case')
