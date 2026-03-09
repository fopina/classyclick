#!/usr/bin/env python3

# README +++
import click


@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet.')
def hello(count, name):
    """Simple program that greets reversed NAME for a total of COUNT times."""
    greet(count, name)


def greet(count, name):
    for _ in range(count):
        click.echo(f'Hello, {reverse(name)}!')


def reverse(name):
    return name[::-1]


# README ---


if __name__ == '__main__':
    hello()
