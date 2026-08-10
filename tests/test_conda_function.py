import os
import sys
import unittest
from unittest.mock import MagicMock, patch

try:
    from conda_subprocess.decorator import conda
    import conda_subprocess.decorator as conda_decorator
    from executorlib import SingleNodeExecutor
    from executorlib.standalone.serialize import cloudpickle_register
    HAS_CONDA_DECORATOR = True
except ImportError:
    HAS_CONDA_DECORATOR = False

    def conda(prefix_name=None, prefix_path=None):
        def wrap_function(funct):
            def function_out(*args, **kwargs):
                return None

            return function_out

        return wrap_function


@conda(prefix_name="py314")
def add_function(parameter_1, parameter_2):
    import os

    return parameter_1 + parameter_2, os.environ["CONDA_PREFIX"]


@conda(prefix_name="py314")
def get_exe(parameter_1, parameter_2):
    import sys

    return parameter_1 + parameter_2, sys.executable


@conda(prefix_name="py314")
def error_funct(parameter_1):
    raise ValueError


class TestCondaFunctionOutput(unittest.TestCase):
    @unittest.skipUnless(HAS_CONDA_DECORATOR, "conda_subprocess dependencies are not available.")
    def test_conda_function_tuple_output(self):
        interface = MagicMock()
        interface.bind_to_random_port.return_value = 2345
        interface.send_and_receive_dict.return_value = (3, "/tmp/py314")
        with patch.object(conda_decorator, "SocketInterface", return_value=interface):
            number, prefix = add_function(parameter_1=1, parameter_2=2)
        self.assertEqual(number, 3)
        self.assertEqual(prefix, "/tmp/py314")
        interface.shutdown.assert_called_once_with(wait=True)


@unittest.skipIf(
    sys.version_info.minor != 14,
    "Test environment has to be Python 3.14 for consistency.",
)
class TestCondaFunction(unittest.TestCase):
    def test_conda_function(self):
        cloudpickle_register(ind=1)
        number, prefix = add_function(parameter_1=1, parameter_2=2)
        self.assertTrue("py314" in prefix.split(os.sep))
        self.assertEqual(number, 3)

    def test_conda_exe_function(self):
        cloudpickle_register(ind=1)
        number, prefix = get_exe(parameter_1=1, parameter_2=2)
        self.assertTrue("py314" in prefix.split(os.sep))
        self.assertEqual(number, 3)

    def test_conda_function_error(self):
        cloudpickle_register(ind=1)
        with self.assertRaises(ValueError):
            error_funct(parameter_1=1)

    def test_conda_function_with_executorlib(self):
        cloudpickle_register(ind=1)
        with SingleNodeExecutor(max_cores=1, hostname_localhost=True) as exe:
            future = exe.submit(add_function, 1, 2)
            number, prefix = future.result()
        self.assertTrue("py314" in prefix.split(os.sep))
        self.assertEqual(number, 3)

    def test_conda_exe_with_executorlib(self):
        cloudpickle_register(ind=1)
        with SingleNodeExecutor(max_cores=1, hostname_localhost=True) as exe:
            future = exe.submit(get_exe, 1, 2)
            number, prefix = future.result()
        self.assertTrue("py314" in prefix.split(os.sep))
        self.assertEqual(number, 3)
