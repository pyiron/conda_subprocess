from unittest import TestCase
from subprocess import PIPE
from conda_subprocess import call, check_call, check_output, run, Popen


class TestCondaSubprocess(TestCase):
    def test_call(self):
        self.assertEqual(call("python --version", prefix_path="../py312"), 0)

    def test_check_call(self):
        self.assertEqual(check_call("python --version", prefix_path="../py312"), 0)

    def test_check_output(self):
        self.assertEqual(check_output("python --version", prefix_path="../py312"), b'Python 3.12.1\n')

    def test_check_output_universal_newlines(self):
        self.assertEqual(check_output("python --version", prefix_path="../py312", universal_newlines=True), 'Python 3.12.1\n')

    def test_run(self):
        self.assertEqual(run("python --version", prefix_path="../py312").returncode, 0)

    def test_popen(self):
        process = Popen("python --version", prefix_path="../py312", stdout=PIPE)
        output = process.communicate()
        self.assertEqual(output[0], b'Python 3.12.1\n')
        self.assertIsNone(output[1])
