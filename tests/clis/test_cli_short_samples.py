from . import CliTestCase


class Test(CliTestCase):
    def test_cli_short_samples(self):
        from ..cli_short_samples import Hello

        result = self.invoker(Hello.click, ['--help'])

        self.assertEqual(
            result.output,
            'Usage: hello [OPTIONS]\n'
            '\n'
            '  Simple program that greets NAME for a total of COUNT times.\n'
            '\n'
            'Options:\n'
            '  --name TEXT          The person to greet.\n'
            '  -c INTEGER           Number of greetings.\n'
            '  --verbose\n'
            '  --weird BOOLEAN\n'
            '  --output PATH\n'
            '  --other-output TEXT\n'
            '  --help               Show this message and exit.\n',
        )
