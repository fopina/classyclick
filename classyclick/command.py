import re
from dataclasses import dataclass


def command(group=None, **click_kwargs):
    if group is None:
        # delay import until required
        import click

        group = click

    def _wrapper(kls):
        if not hasattr(kls, '__bases__'):
            name = getattr(kls, '__name__', str(kls))
            raise ValueError(f'{name} is not a class - classy stands for classes!')

        if 'name' not in click_kwargs:
            # similar to https://github.com/pallets/click/blob/5dd628854c0b61bbdc07f22004c5da8fa8ee9481/src/click/decorators.py#L243C24-L243C60
            # but for expected CamelCase naming in classes
            # TODO: add some tests to this regexp if published ^^
            click_kwargs['name'] = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', kls.__name__).lower()

        def func(**args):
            kls(**args)()

        func.__doc__ = kls.__doc__

        # at the end so it doesn't affect __doc__ or others
        dataclass(kls)
        return group.command(**click_kwargs)(func)

    return _wrapper
