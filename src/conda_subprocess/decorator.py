import subprocess
from concurrent.futures import Future
from socket import gethostname
from typing import Callable, Optional

from executorlib.api import SocketInterface, SubprocessSpawner, get_command_path

from conda_subprocess.process import Popen


class CondaSpawner(SubprocessSpawner):
    def __init__(
        self,
        cwd: Optional[str] = None,
        cores: int = 1,
        openmpi_oversubscribe: bool = False,
        threads_per_core: int = 1,
        prefix_name: Optional[str] = None,
        prefix_path: Optional[str] = None,
    ):
        super().__init__(
            cwd=cwd,
            cores=cores,
            openmpi_oversubscribe=openmpi_oversubscribe,
            threads_per_core=threads_per_core,
        )
        self._prefix_name = prefix_name
        self._prefix_path = prefix_path

    def bootup(
        self,
        command_lst: list[str],
        stop_function: Optional[Callable] = None,
    ) -> bool:
        """
        Method to start the subprocess interface.

        Args:
            command_lst (list[str]): The command list to execute.
            stop_function (Callable): Function to stop the interface.

        Returns:
            bool: Whether the interface was successfully started.
        """
        self._process = Popen(
            args=self.generate_command(command_lst=command_lst),
            cwd=self._cwd,
            stdin=subprocess.DEVNULL,
            prefix_name=self._prefix_name,
            prefix_path=self._prefix_path,
        )
        return self.poll()


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
            interface = SocketInterface(
                spawner=CondaSpawner(
                    cores=1,
                    prefix_name=prefix_name,
                    prefix_path=prefix_path,
                )
            )
            command_lst = [
                "python",
                get_command_path(executable="interactive_serial.py"),
            ]
            if not hostname_localhost:
                command_lst += ["--host", gethostname()]
            command_lst += ["--zmqport", str(interface.bind_to_random_port())]
            interface.bootup(command_lst=command_lst)
            task_future.set_result(
                interface.send_and_receive_dict(input_dict=task_dict)
            )
            interface.shutdown(wait=True)
            return task_future.result()

        return function_wrapped

    return conda_function
