# README +++
from click.testing import CliRunner

# Hello being the example above that reverses name
from .cli_hello import Hello


def test_hello_world():
    runner = CliRunner()
    result = runner.invoke(Hello.click, ['--name', 'Peter'])
    assert result.exit_code == 0
    assert result.output == 'Hello, reteP!\n'


# README ---


def test_hello_world():  # noqa: F811 - remove all these overrides (because of non-reversing demos?) in future PR
    runner = CliRunner()
    result = runner.invoke(Hello.click, ['--name', 'Peter'])
    assert result.exit_code == 0
    assert result.output == 'Hello, Peter!\n'
