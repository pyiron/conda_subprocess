import subprocess
from concurrent.futures import Future
from socket import gethostname
from typing import Callable, Optional

from executorlib.api import SocketInterface, SubprocessSpawner, get_command_path

from conda_subprocess.process import Popen


class CondaSpawner(SubprocessSpawner):
    """
    executorlib `SubprocessSpawner` which starts the worker process with
    `conda_subprocess.Popen()` instead of the regular `subprocess.Popen()`, so the
    worker runs inside the conda environment selected by `prefix_name`/`prefix_path`.

    Args:
        cwd (str): Working directory to start the worker process in.
        cores (int): Number of cores to use for the worker process.
        openmpi_oversubscribe (bool): Whether to oversubscribe the worker process.
        threads_per_core (int): Number of threads per core.
        prefix_name (str): Name of the conda environment the worker process should be
            executed in.
        prefix_path (str): Absolute path of the conda environment the worker process
            should be executed in.
    """

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
    """
    Decorator to execute a python function in a different conda environment, built on
    top of `executorlib`.

    The decorated function (including its arguments and return value) is shipped to a
    worker process running in the target conda environment via `cloudpickle`, so the
    target environment's Python minor version must match the one used to define the
    decorated function.

    Args:
        prefix_name (str): Name of the conda environment the function should be
            executed in, e.g. `"py312"`.
        prefix_path (str): Absolute path of the conda environment the function should
            be executed in.
        hostname_localhost (bool): Use `localhost` instead of the system hostname to
            establish the connection to the worker process. Required in restricted
            network environments such as containers or HPC login nodes where the
            hostname cannot be resolved.

    Returns:
        Callable: Decorator which wraps the given function so it executes in the
            target conda environment.

    Example:
        >>> from conda_subprocess.decorator import conda
        >>> @conda(prefix_name="py312")
        ... def add_function(parameter_1, parameter_2):
        ...     return parameter_1 + parameter_2
        >>> add_function(parameter_1=1, parameter_2=2)
        3
    """

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
