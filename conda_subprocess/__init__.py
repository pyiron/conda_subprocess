from conda_subprocess.process import Popen
from conda_subprocess.interface import call, check_call, check_output, run
from . import _version

__version__ = _version.get_versions()["version"]
__all__ = [
    Popen,
    call,
    check_call,
    check_output,
    run,
]
