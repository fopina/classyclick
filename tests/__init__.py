from functools import cached_property
from unittest import TestCase


class BaseCase(TestCase):
    @cached_property
    def click_version(self):
        from click import __version__

        return tuple(map(int, __version__.split('.')))
