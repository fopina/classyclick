import classyclick
from classyclick import utils
from tests import BaseCase


class Test(BaseCase):
    def test_camel_kebab(self):
        self.assertEqual(utils.camel_kebab('CamelCase'), 'camel-case')
        self.assertEqual(utils.camel_kebab('Case'), 'case')
        self.assertEqual(utils.camel_kebab('Camel123Case'), 'camel123-case')

    def test_snake_kebab(self):
        self.assertEqual(utils.snake_kebab('dry_run'), 'dry-run')

    def test_group_subclass_without_local_annotations_builds_click_command(self):
        class Who(classyclick.Group):
            __config__ = classyclick.Group.Config(name='who')

        self.assertEqual(Who.click.name, 'who')
