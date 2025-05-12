import importlib.metadata
from functools import cached_property
from unittest import TestCase


class BaseCase(TestCase):
    @cached_property
    def click_version(self):
        version = importlib.metadata.version('click')

        return tuple(map(int, version.split('.')))
