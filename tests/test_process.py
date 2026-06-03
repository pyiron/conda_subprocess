import os
import tempfile
from unittest import TestCase
from conda.base.context import (
    context,
)
from conda.exceptions import (
    CondaValueError,
    EnvironmentLocationNotFound,
    EnvironmentNameNotFound,
)
from conda_subprocess.process import (
    _check_prefix,
    _validate_prefix,
    _validate_prefix_name,
    locate_prefix_by_name,
)


class TestProcess(TestCase):
    def test_locate_prefix_by_name(self):
        self.assertEqual(context.root_prefix, locate_prefix_by_name(name="root"))
        with self.assertRaises(EnvironmentNameNotFound):
            locate_prefix_by_name(name="error")

    def test_validate_prefix_name(self):
        self.assertEqual(context.root_prefix, _validate_prefix_name(prefix_name="root", ctx=context, allow_base=True))
        with self.assertRaises(CondaValueError):
            _validate_prefix_name(prefix_name="root", ctx=context, allow_base=False)
        with self.assertRaises(CondaValueError):
            _validate_prefix_name(prefix_name="/", ctx=context, allow_base=True)

    def test_check_prefix_name(self):
        self.assertEqual(context.default_prefix, _check_prefix())

    def test_validate_prefix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_dir = os.path.join(temp_dir, "missing")
            with self.assertRaises(EnvironmentLocationNotFound):
                _validate_prefix(missing_dir)
