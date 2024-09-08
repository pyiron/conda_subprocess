from concurrent.futures import Future
import queue
from unittest import TestCase
from executorlib.shared.interface import SubprocessInterface
from executorlib.shared.executor import cloudpickle_register, get_command_path
from executorlib.shared.communication import interface_bootup


def add_function(parameter_1, parameter_2):
    import importlib

    system = importlib.import_module("sys")

    return (
        parameter_1
        + parameter_2
        + system.version_info.major
        + system.version_info.minor
    )


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
            command_lst=["python", get_command_path(executable="interactive_serial.py")],
            connections=SubprocessInterface(cores=1),
            hostname_localhost=False,
            prefix_path=None,
            prefix_name="py312",
        )
        task_future.set_result(interface.send_and_receive_dict(input_dict=task_dict))
        interface.shutdown(wait=True)
        self.assertEqual(task_future.result(), 18)
