import os
from subprocess import Popen

from conda.auxlib.compat import shlex_split_unicode
from conda.base.context import context, validate_prefix_name
from conda.cli.common import validate_prefix
from conda.common.compat import encode_arguments, encode_environment, isiterable
from conda.common.path import expand
from conda.gateways.subprocess import subprocess_call
from conda.utils import wrap_subprocess_call


def conda_subprocess_call(args, cwd, prefix_name=None, prefix_path=None):
    """

    Args:
        args:
        cwd:
        prefix_name (str / None): Name of the conda environment
        prefix_path (str / None): Path of the conda environment

    Returns:

    """
    return subprocess_call(
        command=wrap_subprocess_call(
            root_prefix=context.root_prefix,
            prefix=validate_prefix(  # ensure prefix exists
                prefix=_check_prefix(
                    prefix_name=prefix_name,
                    prefix_path=prefix_path,
                )
            ),
            dev_mode=False,
            debug_wrapper_scripts=False,
            arguments=_check_args(args=args),
            use_system_tmp_path=True,
        )[1],
        env=encode_environment(os.environ.copy()),
        path=cwd,
        raise_on_error=True,
        capture_output=True,
    )


def conda_subprocess_popen(
    args,
    bufsize=-1,
    stdin=None,
    stdout=None,
    stderr=None,
    preexec_fn=None,
    close_fds=True,
    cwd=None,
    prefix_name=None,
    prefix_path=None,
    universal_newlines=None,
    startupinfo=None,
    creationflags=0,
    restore_signals=True,
    start_new_session=False,
    pass_fds=(),
    user=None,
    group=None,
    extra_groups=None,
    encoding=None,
    errors=None,
    text=None,
    umask=-1,
    pipesize=-1,
    process_group=None
):
    # create run script
    script, command = wrap_subprocess_call(
        root_prefix=context.root_prefix,
        prefix=validate_prefix(
            prefix=_check_prefix(
                prefix_name=prefix_name,
                prefix_path=prefix_path,
            )
        ),  # ensure prefix exists
        dev_mode=False,
        debug_wrapper_scripts=False,
        arguments=_check_args(args=args),
        use_system_tmp_path=True,
    )

    if not isiterable(command):
        command = shlex_split_unicode(command)

    # spawn subprocess
    return Popen(
        args=encode_arguments(command),
        bufsize=bufsize,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        preexec_fn=preexec_fn,
        close_fds=close_fds,
        shell=False,
        cwd=cwd,
        env=encode_environment(os.environ.copy()),
        universal_newlines=universal_newlines,
        startupinfo=startupinfo,
        creationflags=creationflags,
        restore_signals=restore_signals,
        start_new_session=start_new_session,
        pass_fds=pass_fds,
        user=user,
        group=group,
        extra_groups=extra_groups,
        encoding=encoding,
        errors=errors,
        text=text,
        umask=umask,
        pipesize=pipesize,
        process_group=process_group
    )


def _check_prefix(prefix_name=None, prefix_path=None):
    if prefix_name is None and prefix_path is None:
        return context.default_prefix
    elif prefix_path is not None:
        return expand(prefix_path)
    else:
        return validate_prefix_name(prefix_name, ctx=context)


def _check_args(args):
    if isinstance(args, str):
        return args.split()
    else:
        return args
