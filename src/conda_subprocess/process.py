import os
from subprocess import Popen as subprocess_Popen

from conda.auxlib.compat import shlex_split_unicode
from conda.auxlib.ish import dals
from conda.base.context import (
    PREFIX_NAME_DISALLOWED_CHARS,
    ROOT_ENV_NAME,
    Context,
    _first_writable_envs_dir,
    context,
)
from conda.cli.common import validate_prefix
from conda.common.compat import encode_environment, isiterable
from conda.common.path import expand
from conda.exceptions import CondaValueError, EnvironmentNameNotFound
from conda.utils import wrap_subprocess_call


def Popen(
    args,
    bufsize=-1,
    stdin=None,
    stdout=None,
    stderr=None,
    preexec_fn=None,
    close_fds=True,
    cwd=None,
    env=None,
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

    # update environment
    environment_dict = os.environ.copy()
    if env is not None:
        environment_dict.update(env)

    # spawn subprocess
    return subprocess_Popen(
        args=command,
        bufsize=bufsize,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        preexec_fn=preexec_fn,
        close_fds=close_fds,
        shell=False,
        cwd=cwd,
        env=encode_environment(environment_dict),
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
    )


def _check_prefix(prefix_name=None, prefix_path=None):
    if prefix_name is None and prefix_path is None:
        return context.default_prefix
    elif prefix_path is not None:
        return expand(prefix_path)
    else:
        return _validate_prefix_name(prefix_name, ctx=context)


def _check_args(args):
    if isinstance(args, str):
        return args.split()
    else:
        return args


def _locate_prefix_by_name(name, envs_dirs=None):
    """
    Find the location of a prefix given a conda env name.
    If the location does not exist, an error is raised.
    """
    assert name
    if name in (ROOT_ENV_NAME, "root"):
        return context.root_prefix
    if envs_dirs is None:
        envs_dirs = context.envs_dirs
    for envs_dir in envs_dirs:
        if not os.path.isdir(envs_dir):
            continue
        prefix = os.path.join(envs_dir, name)
        if os.path.isdir(prefix):
            return os.path.abspath(prefix)
    raise EnvironmentNameNotFound(name)


def _validate_prefix_name(prefix_name: str, ctx: Context, allow_base=True) -> str:
    """Run various validations to make sure prefix_name is valid"""
    if PREFIX_NAME_DISALLOWED_CHARS.intersection(prefix_name):
        raise CondaValueError(
            dals(
                f"""
                Invalid environment name: {prefix_name!r}
                Characters not allowed: {PREFIX_NAME_DISALLOWED_CHARS}
                If you are specifying a path to an environment, the `-p`
                flag should be used instead.
                """
            )
        )

    if prefix_name in (ROOT_ENV_NAME, "root"):
        if allow_base:
            return ctx.root_prefix
        else:
            raise CondaValueError(
                "Use of 'base' as environment name is not allowed here."
            )

    else:
        envs_dirs = context.envs_dirs
        envs_dirs += (
            os.path.abspath(os.path.join(os.environ["CONDA_EXE"], "..", "..", "envs")),
        )
        try:
            return _locate_prefix_by_name(name=prefix_name, envs_dirs=envs_dirs)
        except EnvironmentNameNotFound:
            return os.path.join(_first_writable_envs_dir(), prefix_name)
