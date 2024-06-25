import os
from subprocess import PIPE
from unittest import TestCase

from conda.base.context import context
from conda_subprocess import call, check_call, check_output, run, Popen


class TestCondaSubprocess(TestCase):
    def setUpClass(cls):
        cls.env_name = "py312"
        cls.env_path = os.path.join(context.root_prefix, "..", cls.env_name)

    def test_call_path(self):
        self.assertEqual(call("python --version", prefix_path=self.env_path), 0)

    def test_call_name(self):
        self.assertEqual(call("python --version", prefix_name=self.env_name), 0)

    def test_check_call_path(self):
        self.assertEqual(check_call("python --version", prefix_path=self.env_path), 0)

    def test_check_call_name(self):
        self.assertEqual(check_call("python --version", prefix_name=self.env_name), 0)

    def test_check_output_path(self):
        if os.name == "nt":
            self.assertEqual(
                check_output("python --version", prefix_path=self.env_path),
                b"Python 3.12.1\r\n",
            )
        else:
            self.assertEqual(
                check_output("python --version", prefix_path=self.env_path),
                b"Python 3.12.1\n",
            )

    def test_check_output_name(self):
        if os.name == "nt":
            self.assertEqual(
                check_output("python --version", prefix_name=self.env_name),
                b"Python 3.12.1\r\n",
            )
        else:
            self.assertEqual(
                check_output("python --version", prefix_name=self.env_name),
                b"Python 3.12.1\n",
            )

    def test_check_output_universal_newlines(self):
        self.assertEqual(
            check_output(
                "python --version", prefix_path=self.env_path, universal_newlines=True
            ),
            "Python 3.12.1\n",
        )

    def test_run_path(self):
        self.assertEqual(
            run("python --version", prefix_path=self.env_path).returncode, 0
        )

    def test_run_name(self):
        self.assertEqual(
            run("python --version", prefix_name=self.env_name).returncode, 0
        )

    def test_popen_path(self):
        process = Popen("python --version", prefix_path=self.env_path, stdout=PIPE)
        output = process.communicate()
        if os.name == "nt":
            self.assertEqual(output[0], b"Python 3.12.1\r\n")
        else:
            self.assertEqual(output[0], b"Python 3.12.1\n")
        self.assertIsNone(output[1])

    def test_popen_name(self):
        process = Popen("python --version", prefix_name=self.env_name, stdout=PIPE)
        output = process.communicate()
        if os.name == "nt":
            self.assertEqual(output[0], b"Python 3.12.1\r\n")
        else:
            self.assertEqual(output[0], b"Python 3.12.1\n")
        self.assertIsNone(output[1])

    def test_environment_variable(self):
        self.assertTrue(
            "TESTVAR=test"
            in check_output(
                "env",
                prefix_path=self.env_path,
                env={"TESTVAR": "test"},
                universal_newlines=True,
            ).split("\n"),
        )
