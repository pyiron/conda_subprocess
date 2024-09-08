from concurrent.futures import Future
import queue
from unittest import TestCase
from executorlib.shared.executor import execute_parallel_tasks
from executorlib.shared.interface import SubprocessInterface
from executorlib.shared.executor import cloudpickle_register


def add_function(parameter_1, parameter_2):
    import sys
    return parameter_1 + parameter_2 + sys.version_info.major + sys.version_info.minor


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
            max_cores=1,
            hostname_localhost=False,
            prefix_name="py312",
        )
        self.assertEqual(task_future.result(), 18)
