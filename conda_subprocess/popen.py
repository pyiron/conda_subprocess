import os
from subprocess import Popen

from conda.auxlib.compat import shlex_split_unicode
from conda.base.context import context, validate_prefix_name
from conda.common.compat import encode_arguments, encode_environment, isiterable
from conda.utils import wrap_subprocess_call
from conda.common.path import expand
from conda.cli.common import validate_prefix


def conda_subprocess_popen(
    args,
    bufsize=-1,
    stdin=None,
    stdout=None,
    stderr=None,
    preexec_fn=None,
    close_fds=True,
    shell=False,
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
        shell=shell,
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
