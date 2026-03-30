#!/usr/bin/env python3
"""cli not with classy but with click, to verify some behaviors"""

import click

import classyclick


# README +++
class Greet(classyclick.Group):
    """Greeting commands."""

    debug: bool = classyclick.Option('--debug/--no-debug')

    def __call__(self):
        click.echo(f'Debug mode is {"on" if self.debug else "off"}')


class Hello(Greet.Command):
    """Say hello."""

    __config__ = classyclick.Command.Config(group=Greet)

    name: str = classyclick.Option(prompt='Your name')

    def __call__(self):
        click.echo(f'Hello, {self.name}!')


# README ---


@click.command()
@click.argument('src')
@click.argument('dest', required=False)
@click.decorators.pass_context
@click.decorators.pass_obj
def clone(obj, ctx, src, dest):
    print(obj, ctx, src, dest)


if __name__ == '__main__':
    clone()
