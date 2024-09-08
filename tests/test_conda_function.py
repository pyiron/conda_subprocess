from concurrent.futures import Future
import queue
import sys
from unittest import TestCase, skipIf
from executorlib.shared.interface import SubprocessInterface
from executorlib.shared.executor import cloudpickle_register, get_command_path
from executorlib.shared.communication import interface_bootup


def add_function(parameter_1, parameter_2):
    import os

    return (
        parameter_1 + parameter_2,
        os.environ["CONDA_PREFIX"]
    )


skipIf(sys.version_info.minor != 12, "Test environment has to be Python 3.12 for consistency.")
class TestCondaFunction(TestCase):
    def test_conda_function(self):
        cloudpickle_register(ind=1)
        task_queue = queue.Queue()
        task_future = Future()
        task_dict = {
            "fn": add_function,
            "args": (),
            "kwargs": {"parameter_1": 1, "parameter_2": 2},
            "resource_dict": {"cores": 1},
        }
        task_queue.put({"shutdown": True, "wait": True})
        interface = interface_bootup(
            command_lst=[
                "python",
                get_command_path(executable="interactive_serial.py"),
            ],
            connections=SubprocessInterface(cores=1),
            hostname_localhost=False,
            prefix_path=None,
            prefix_name="py312",
        )
        task_future.set_result(interface.send_and_receive_dict(input_dict=task_dict))
        interface.shutdown(wait=True)
        number, prefix = task_future.result()
        self.assertEqual(prefix[-5:], "py312")
        self.assertEqual(number, 3)
