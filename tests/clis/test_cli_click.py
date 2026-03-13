from . import CliTestCase


class Test(CliTestCase):
    def test_cli_click(self):
        from ..cli_click import clone

        result = self.invoker(clone, ['--help'])

        self.assertEqual(
            result.output, 'Usage: clone [OPTIONS] SRC [DEST]\n\nOptions:\n  --help  Show this message and exit.\n'
        )
