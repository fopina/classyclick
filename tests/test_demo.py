import unittest

import classyclick.demo


class Test(unittest.TestCase):
    # TODO: update with your own unit tests and assertions
    def test_echo(self):
        self.assertEqual(classyclick.demo.echo('hey'), 'HEY right back at ya!')
