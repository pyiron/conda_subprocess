from concurrent.futures import Future
import queue
from unittest import TestCase
from executorlib.shared.interface import SubprocessInterface
from executorlib.shared.executor import cloudpickle_register, get_command_path
from executorlib.shared.communication import interface_bootup


def add_function(parameter_1, parameter_2):
    import importlib
    system = importlib.import_module('sys')

    return parameter_1 + parameter_2 + system.version_info.major + system.version_info.minor


def execute_parallel_tasks(
    future_queue,
    cores,
    interface_class,
    hostname_localhost=False,
    prefix_name=None,
    prefix_path=None,
    **kwargs,
) -> None:
    """
    Execute a single tasks in parallel using the message passing interface (MPI).

    Args:
       future_queue (queue.Queue): task queue of dictionary objects which are submitted to the parallel process
       cores (int): defines the total number of MPI ranks to use
       interface_class (BaseInterface): Interface to start process on selected compute resources
       hostname_localhost (boolean): use localhost instead of the hostname to establish the zmq connection. In the
                                     context of an HPC cluster this essential to be able to communicate to an
                                     Executor running on a different compute node within the same allocation. And
                                     in principle any computer should be able to resolve that their own hostname
                                     points to the same address as localhost. Still MacOS >= 12 seems to disable
                                     this look up for security reasons. So on MacOS it is required to set this
                                     option to true
       prefix_name (str): name of the conda environment to initialize
       prefix_path (str): path of the conda environment to initialize
    """
    interface = interface_bootup(
        command_lst=["python", get_command_path(executable="interactive_serial.py")],
        connections=interface_class(cores=cores, **kwargs),
        hostname_localhost=hostname_localhost,
        prefix_path=prefix_path,
        prefix_name=prefix_name,
    )
    while True:
        task_dict = future_queue.get()
        if "shutdown" in task_dict.keys() and task_dict["shutdown"]:
            interface.shutdown(wait=task_dict["wait"])
            future_queue.task_done()
            future_queue.join()
            break
        elif "fn" in task_dict.keys() and "future" in task_dict.keys():
            f = task_dict.pop("future")
            if f.set_running_or_notify_cancel():
                try:
                    f.set_result(interface.send_and_receive_dict(input_dict=task_dict))
                except Exception as thread_exception:
                    interface.shutdown(wait=True)
                    future_queue.task_done()
                    f.set_exception(exception=thread_exception)
                    raise thread_exception
                else:
                    future_queue.task_done()


class TestCondaFunction(TestCase):
    def test_conda_function(self):
        cloudpickle_register(ind=1)
        task_queue = queue.Queue()
        task_future = Future()
        task_queue.put(
            {
                "fn": add_function,
                "args": (),
                "kwargs": {"parameter_1": 1, "parameter_2": 2},
                "future": task_future,
                "resource_dict": {"cores": 1},
            }
        )
        task_queue.put({"shutdown": True, "wait": True})
        execute_parallel_tasks(
            future_queue=task_queue,
            interface_class=SubprocessInterface,
            cores=1,
            hostname_localhost=False,
            prefix_name="py312",
        )
        self.assertEqual(task_future.result(), 18)
