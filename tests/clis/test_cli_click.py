from . import CliTestCase, load_cli_script


class Test(CliTestCase):
    def test_cli_click(self):
        module = load_cli_script('cli_click.py')

        result = self.invoker(module.clone, ['--help'])

        self.assertEqual(
            result.output, 'Usage: clone [OPTIONS] SRC [DEST]\n\nOptions:\n  --help  Show this message and exit.\n'
        )
