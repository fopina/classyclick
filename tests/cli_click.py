"""cli not with classy but with click, to verify some behaviors"""

import click


@click.command()
@click.argument('src')
@click.argument('dest', required=False)
@click.decorators.pass_context
@click.decorators.pass_obj
def clone(obj, ctx, src, dest):
    print(obj, ctx, src, dest)


if __name__ == '__main__':
    clone()
