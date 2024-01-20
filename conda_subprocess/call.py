import os

from conda.base.context import context, validate_prefix_name
from conda.common.compat import encode_environment
from conda.utils import wrap_subprocess_call
from conda.common.path import expand
from conda.cli.common import validate_prefix
from conda.gateways.subprocess import subprocess_call


def conda_subprocess_call(args, cwd, prefix_name=None, prefix_path=None):
    """

    Args:
        args:
        cwd:
        prefix_name (str / None): Name of the conda environment
        prefix_path (str / None): Path of the conda environment

    Returns:

    """
    if prefix_name is None and prefix_path is None:
        prefix = context.default_prefix
    elif prefix_path is not None:
        prefix = expand(prefix_path)
    else:
        prefix = validate_prefix_name(prefix_name, ctx=context)

    # create run script
    script, command = wrap_subprocess_call(
        root_prefix=context.root_prefix,
        prefix=validate_prefix(prefix=prefix),  # ensure prefix exists
        dev_mode=False,
        debug_wrapper_scripts=False,
        arguments=args,
        use_system_tmp_path=True,
    )

    # run script
    return subprocess_call(
        command=command,
        env=encode_environment(os.environ.copy()),
        path=cwd,
        raise_on_error=True,
        capture_output=True,
    )
