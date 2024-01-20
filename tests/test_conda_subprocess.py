import os
from subprocess import PIPE
from unittest import TestCase

from conda.base.context import context
from conda_subprocess import call, check_call, check_output, run, Popen


class TestCondaSubprocess(TestCase):
    def setUp(self):
        self.env_path = os.path.join(context.root_prefix, "..", "py312")

    def test_call(self):
        self.assertEqual(call("python --version", prefix_path=self.env_path), 0)

    def test_check_call(self):
        self.assertEqual(check_call("python --version", prefix_path=self.env_path), 0)

    def test_check_output(self):
        if os.name == "nt":
            self.assertEqual(check_output("python --version", prefix_path=self.env_path), b'Python 3.12.1\r\n')
        else:
            self.assertEqual(check_output("python --version", prefix_path=self.env_path), b'Python 3.12.1\n')

    def test_check_output_universal_newlines(self):
        self.assertEqual(check_output("python --version", prefix_path=self.env_path, universal_newlines=True), 'Python 3.12.1\n')

    def test_run(self):
        self.assertEqual(run("python --version", prefix_path=self.env_path).returncode, 0)

    def test_popen(self):
        process = Popen("python --version", prefix_path=self.env_path, stdout=PIPE)
        output = process.communicate()
        if os.name == "nt":
            self.assertEqual(output[0], b'Python 3.12.1\r\n')
        else:
            self.assertEqual(output[0], b'Python 3.12.1\n')
        self.assertIsNone(output[1])
