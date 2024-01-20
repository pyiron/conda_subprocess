# Run subprocess in a different conda environment

## Example 
Create a new conda environment - in this example a conda environment for Python 3.12:
```commandline
conda create -n py312 python=3.12 
```

### Call Function 
Open a python shell in your base environment where `conda_subprocess` is installed:
```python
from conda_subprocess import conda_subprocess_call
conda_subprocess_call(["python", "--version"], cwd=".", prefix_name="py312")
>>> Response(stdout='Python 3.12.1\n', stderr='', rc=0)
```

### Popen Function 
For interactive communication between the conda environments `conda_subprocess` implements the `Popen` interface:
```python
from subprocess import PIPE
from conda_subprocess import conda_subprocess_popen
process = conda_subprocess_popen(args=["python", "--version"], stdout=PIPE, prefix_name="py312")
process.communicate()
>>> (b'Python 3.12.1\n', None)
```

In addition to specifying the environment based on the `prefix_name`, it is also possible to specify the `prefix_path`:
```python
from subprocess import PIPE
from conda_subprocess import conda_subprocess_popen
process = conda_subprocess_popen(args=["python", "--version"], stdout=PIPE, prefix_path="/Users/janssen/mambaforge/envs/py312")
process.communicate()
>>> (b'Python 3.12.1\n', None)
```

### Remarks
* The `shell` parameter and the `env` parameter are not supported in `conda_subprocess_popen()`. 