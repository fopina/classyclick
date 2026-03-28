from tests.autodiscover_fixtures.commands.admin import Are


class You(Are.Command):
    """you"""

    def __call__(self): ...
