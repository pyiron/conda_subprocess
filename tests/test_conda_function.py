import sys
import unittest

try:
    from conda_subprocess.decorator import conda
    from executorlib import Executor
    from executorlib.standalone.serialize import cloudpickle_register
except ImportError:

    def conda(prefix_name=None, prefix_path=None):
        def wrap_function(funct):
            def function_out(*args, **kwargs):
                return None

            return function_out

        return wrap_function


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

    def test_conda_function_with_executorlib(self):
        cloudpickle_register(ind=1)
        with Executor(max_cores=1, backend="local", hostname_localhost=True) as exe:
            future = exe.submit(add_function, 1, 2)
            number, prefix = future.result()
        self.assertEqual(prefix[-5:], "py312")
        self.assertEqual(number, 3)
