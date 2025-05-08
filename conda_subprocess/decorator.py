import subprocess
from concurrent.futures import Future
from socket import gethostname
from typing import Optional

from executorlib.api import SocketInterface, SubprocessSpawner, get_command_path

from conda_subprocess.process import Popen


def conda(
    prefix_name: Optional[str] = None,
    prefix_path: Optional[str] = None,
    hostname_localhost: bool = False,
):
    def conda_function(funct):
        def function_wrapped(*args, **kwargs):
            task_future = Future()
            task_dict = {
                "fn": funct,
                "args": args,
                "kwargs": kwargs,
                "resource_dict": {"cores": 1},
            }
            interface = SocketInterface(spawner=SubprocessSpawner(cores=1))
            command_lst = [
                "python",
                get_command_path(executable="interactive_serial.py"),
            ]
            if not hostname_localhost:
                command_lst += ["--host", gethostname()]
            command_lst += ["--zmqport", str(interface.bind_to_random_port())]
            interface._spawner._process = Popen(
                args=interface._spawner.generate_command(command_lst=command_lst),
                cwd=interface._spawner._cwd,
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
