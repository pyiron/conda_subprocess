import os
from subprocess import PIPE, CalledProcessError
from unittest import TestCase

from conda.base.context import context
from conda_subprocess import call, check_call, check_output, run, Popen


class TestCondaSubprocess(TestCase):
    @classmethod
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
        expected_output = (
            b"Python 3.12.1\r\n" if os.name == "nt" else b"Python 3.12.1\n"
        )
        self.assertEqual(
            check_output("python --version", prefix_path=self.env_path),
            expected_output,
        )

    def test_check_output_name(self):
        expected_output = (
            b"Python 3.12.1\r\n" if os.name == "nt" else b"Python 3.12.1\n"
        )
        self.assertEqual(
            check_output("python --version", prefix_name=self.env_name),
            expected_output,
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
        expected_output = (
            b"Python 3.12.1\r\n" if os.name == "nt" else b"Python 3.12.1\n"
        )
        process = Popen("python --version", prefix_path=self.env_path, stdout=PIPE)
        output = process.communicate()
        self.assertEqual(output[0], expected_output)
        self.assertIsNone(output[1])

    def test_popen_name(self):
        expected_output = (
            b"Python 3.12.1\r\n" if os.name == "nt" else b"Python 3.12.1\n"
        )
        process = Popen("python --version", prefix_name=self.env_name, stdout=PIPE)
        output = process.communicate()
        self.assertEqual(output[0], expected_output)
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

    def test_check_output_error(self):
        with self.assertRaises(CalledProcessError):
            check_output(
                "exit 1",
                prefix_path=self.env_path,
                universal_newlines=True,
            )

    def test_check_output_kwargs_error(self):
        with self.assertRaises(ValueError):
            check_output(
                "exit 1",
                prefix_path=self.env_path,
                universal_newlines=True,
                stdout="test.out"
            )

    def test_call_timeout(self):
        with self.assertRaises(ValueError):
            call(
                "sleep 5",
                timeout=1,
                prefix_path=self.env_path,
                universal_newlines=True,
            )
