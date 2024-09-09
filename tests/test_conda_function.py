import sys
import unittest

try:
    from executorlib.shared.executor import cloudpickle_register
except ImportError:
    pass


from conda_subprocess.decorator import conda


@conda(prefix_name="py312")
def add_function(parameter_1, parameter_2):
    import os

    return (parameter_1 + parameter_2, os.environ["CONDA_PREFIX"])


@unittest.skipIf(
    sys.version_info.minor != 12,
    "Test environment has to be Python 3.12 for consistency.",
)
class TestCondaFunction(unittest.TestCase):
    def test_conda_function(self):
        cloudpickle_register(ind=1)
        number, prefix = add_function(parameter_1=1, parameter_2=2)
        self.assertEqual(prefix[-5:], "py312")
        self.assertEqual(number, 3)
