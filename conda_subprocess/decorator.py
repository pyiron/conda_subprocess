import subprocess
from concurrent.futures import Future
from socket import gethostname
from typing import Optional

from executorlib.shared.communication import SocketInterface
from executorlib.shared.executor import get_command_path
from executorlib.shared.interface import SubprocessInterface

from conda_subprocess.process import Popen


def conda(prefix_name: Optional[str] = None, prefix_path: Optional[str] = None):
    def conda_function(funct):
        def function_wrapped(*args, **kwargs):
            task_future = Future()
            task_dict = {
                "fn": funct,
                "args": args,
                "kwargs": kwargs,
                "resource_dict": {"cores": 1},
            }
            interface = SocketInterface(interface=SubprocessInterface(cores=1))
            command_lst = [
                "python",
                get_command_path(executable="interactive_serial.py"),
                "--host",
                gethostname(),
                "--zmqport",
                str(interface.bind_to_random_port()),
            ]
            interface._interface._process = Popen(
                args=interface._interface.generate_command(command_lst=command_lst),
                cwd=interface._interface._cwd,
                stdin=subprocess.DEVNULL,
                prefix_name=prefix_name,
                prefix_path=prefix_path,
            )
            task_future.set_result(
                interface.send_and_receive_dict(input_dict=task_dict)
            )
            interface.shutdown(wait=True)
            return task_future.result()

        return function_wrapped

    return conda_function
