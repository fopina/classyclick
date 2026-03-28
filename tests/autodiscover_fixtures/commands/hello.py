from tests.autodiscover_fixtures.cli import Who


class Ami(Who.Command):
    """ami"""

    def __call__(self): ...
