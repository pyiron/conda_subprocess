# conda subprocess
Run a subprocess in a different conda environment. 

## Example 
Create a new conda environment - in this example a conda environment for Python 3.12:
```commandline
conda create -n py312 python=3.12 
```

Open a python shell in your base environment where `conda_subprocess` is installed and execute `python --version` in the
`py312` environment:
```python
from conda_subprocess import check_output
check_output("python --version", prefix_name="py312")
>>> b'Python 3.12.1\n'
```

Alternatively, the environment can be specified with the absolute path:
```python
from conda_subprocess import check_output
check_output("python --version", prefix_path="/Users/janssen/mambaforge/envs/py312")
>>> b'Python 3.12.1\n'
```

As expected the process for the arguments for the subprocess call can also be defined as list:
```python
from conda_subprocess import check_output
check_output(["python", "--version"], prefix_path="/Users/janssen/mambaforge/envs/py312")
>>> b'Python 3.12.1\n'
```

In addition to the `check_output()` function also the `check_call()` function is implemented:
```python
from conda_subprocess import check_call
check_call("python --version", prefix_name="py312")
>>> Python 3.12.1
>>> 0
```

As well as the `call()` function:
```python
from conda_subprocess import call
call("python --version", prefix_name="py312")
>>> Python 3.12.1
>>> 0
```

And the `run()` function:
```python
from conda_subprocess import run
run("python --version", prefix_name="py312")
>>> Python 3.12.1
>>> CompletedProcess(args=['/bin/bash', '/var/folders/9p/rztyv06d0xv4h26cyv8nrw3m0000gq/T/tmpm8b8i0r3'], returncode=0)
```
As the `CompletedProcess` arguments illustrate `conda_subprocess` is internally writing the commands to a temporary file
for execution, to guarantee the conda environment is correctly activated.

For interactive communication `conda_subprocess` implements the `Popen` interface:
```python
from subprocess import PIPE
from conda_subprocess import Popen
process = Popen(["python", "--version"], stdout=PIPE, prefix_name="py312")
process.communicate()
>>> (b'Python 3.12.1\n', None)
```

## Remarks
* The `shell` parameter and the `env` parameter are not supported in `conda_subprocess_popen()`. 