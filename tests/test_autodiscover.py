from click.testing import CliRunner

from classyclick.helpers import discover_commands
from tests import BaseCase
from tests.autodiscover_fixtures.cli import Who


class Test(BaseCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_discover_commands_loads_group_commands_recursively(self):
        result = self.runner.invoke(Who.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: who [OPTIONS] COMMAND [ARGS]...

  autodiscover fixture root

Options:
  --help  Show this message and exit.
""",
        )

        discover_commands('tests.autodiscover_fixtures.commands')

        result = self.runner.invoke(Who.click, args=['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: who [OPTIONS] COMMAND [ARGS]...

  autodiscover fixture root

Options:
  --help  Show this message and exit.

Commands:
  ami  ami
  are  are
""",
        )

        result = self.runner.invoke(Who.click, args=['are', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            """\
Usage: who are [OPTIONS] COMMAND [ARGS]...

  are

Options:
  --help  Show this message and exit.

Commands:
  they  they
  you   you
""",
        )
