from unittest import TestCase
from conda.base.context import (
    context,
)
from conda.exceptions import EnvironmentNameNotFound, CondaValueError
from conda_subprocess.process import _locate_prefix_by_name, _check_prefix, _validate_prefix_name


class TestProcess(TestCase):
    def test_locate_prefix_by_name(self):
        self.assertEqual(context.root_prefix, _locate_prefix_by_name(name="root"))
        self.assertEqual("py312", _locate_prefix_by_name(name="py312"))
        with self.assertRaises(EnvironmentNameNotFound):
            _locate_prefix_by_name(name="error")

    def test_validate_prefix_name(self):
        self.assertEqual(context.root_prefix, _validate_prefix_name(prefix_name="root", ctx=context, allow_base=True))
        with self.assertRaises(CondaValueError):
            _validate_prefix_name(prefix_name="root", ctx=context, allow_base=False)
        with self.assertRaises(EnvironmentNameNotFound):
            _validate_prefix_name(prefix_name="error", ctx=context, allow_base=True)
        with self.assertRaises(CondaValueError):
            _validate_prefix_name(prefix_name="-", ctx=context, allow_base=True)

    def test_check_prefix_name(self):
        self.assertEqual(context.default_prefix, _check_prefix())
