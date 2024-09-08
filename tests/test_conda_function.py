from concurrent.futures import Future
import queue
from socket import gethostname
import subprocess
import sys
import unittest

from executorlib.shared.interface import SubprocessInterface
from executorlib.shared.executor import cloudpickle_register, get_command_path
from executorlib.shared.communication import SocketInterface

import conda_subprocess


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
        task_queue = queue.Queue()
        task_future = Future()
        task_dict = {
            "fn": add_function,
            "args": (),
            "kwargs": {"parameter_1": 1, "parameter_2": 2},
            "resource_dict": {"cores": 1},
        }
        task_queue.put({"shutdown": True, "wait": True})
        interface = SocketInterface(interface=SubprocessInterface(cores=1))
        command_lst = [
            "python",
            get_command_path(executable="interactive_serial.py"),
            "--host",
            gethostname(),
            "--zmqport",
            str(interface.bind_to_random_port()),
        ]
        interface._interface._process = conda_subprocess.Popen(
            args=interface._interface.generate_command(command_lst=command_lst),
            cwd=interface._interface._cwd,
            stdin=subprocess.DEVNULL,
            prefix_name="py312",
        )
        task_future.set_result(interface.send_and_receive_dict(input_dict=task_dict))
        interface.shutdown(wait=True)
        number, prefix = task_future.result()
        self.assertEqual(prefix[-5:], "py312")
        self.assertEqual(number, 3)
