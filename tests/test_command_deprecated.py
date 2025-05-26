import click
from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
    def test_all(self):
        @click.group()
        @click.option('--country', default='Somewhere')
        @click.pass_context
        def cli(ctx, country):
            ctx.obj = dict(country=country)
            ctx.meta['country'] = country

        @classyclick.command(group=cli)
        class Hello:
            name: str = classyclick.argument()
            age: int = classyclick.option(required=True, help='Age')
            country: str = classyclick.context_meta('country')
            obj: any = classyclick.context_obj()
            ctx: any = classyclick.context()

            def __call__(self):
                print(f'Hello, {self.name} from {self.country}, you will be {self.age + 1} next year')

        runner = CliRunner()
        result = runner.invoke(cli, ['hello', 'Peter', '--age', '10'])
        self.assertEqual(result.exception, None)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Hello, Peter from Somewhere, you will be 11 next year\n')
