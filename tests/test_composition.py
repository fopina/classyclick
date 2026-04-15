import sys
from dataclasses import dataclass

from click.testing import CliRunner

import classyclick
from tests import BaseCase


class Test(BaseCase):
    def test_subclassing_argument_after_base_option_keeps_working(self):
        """https://github.com/fopina/classyclick/issues/34"""

        class Base(classyclick.Command):
            base_arg: str = classyclick.Argument()
            base_opt: str = classyclick.Option(default='foo')

            def __call__(self):
                return None

        class Child(Base):
            child_arg: str = classyclick.Argument()
            child_opt: str = classyclick.Option(default='bar')

            def __call__(self):
                print(f'{self.base_arg}:{self.base_opt}:{self.child_arg}:{self.child_opt}')

        direct = Child('base', child_arg='child')
        self.assertEqual(direct.base_arg, 'base')
        self.assertEqual(direct.base_opt, 'foo')
        self.assertEqual(direct.child_arg, 'child')
        self.assertEqual(direct.child_opt, 'bar')

        with self.assertRaisesRegex(TypeError, 'takes 3 positional arguments but 4 were given'):
            Child('base', 'foo', 'child')

        with self.assertRaisesRegex(TypeError, "missing 1 required positional argument: 'child_arg'"):
            Child('base', 'foo')

        result = CliRunner().invoke(Child.click, ['base', 'child'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'base:foo:child:bar\n')

    def test_command_supports_dataclass_mixin_with_classyclick_option(self):
        """https://github.com/fopina/classyclick/issues/71"""
        if sys.version_info < (3, 10):
            self.skipTest('dataclass kw_only requires Python 3.10+')

        @dataclass(kw_only=True)
        class BaseMixin:
            debug: bool = classyclick.Option()

        class FixMe(classyclick.Command, BaseMixin):
            some_flag: bool = classyclick.Option()

            def __call__(self):
                print(f'debug={self.debug} some_flag={self.some_flag}')

        result = CliRunner().invoke(FixMe.click, ['--debug', '--some-flag'])
        self.assertEqual(result.exit_code, 0, result.exception or result.output)
