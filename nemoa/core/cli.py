# -*- coding: utf-8 -*-
"""Command line interface."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import getopt
import sys
from typing import Any, Callable
from nemoa.base import env
from nemoa.core import ui
from nemoa.core.ui import shell
import nemoa.test
import nemoa

def print_scripts(workspace: str) -> None:
    """Print list of scripts to standard output."""
    nemoa.set('mode', 'silent')

    if nemoa.open(workspace):
        ui.info('Scripts in workspace %s:\n' % (nemoa.get('workspace')))
        for script in nemoa.list('scripts'):
            ui.info('    %s' % (script))
        ui.info('')

def print_usage() -> None:
    """Print script usage to standard output."""
    ui.info("Usage: nemoa [options]\n\n"
        "Options:\n\n"
        "    -h --help         "
        "      Print this\n"
        "    -s --shell        "
        "      Start nemoa session in IPython interactive shell\n"
        "    -l --list         "
        "      List workspaces\n"
        "    -w --workspace    "
        "      List scripts in workspace\n"
        "    -r --run-script   "
        "      Open workspace and execute script\n"
        "    -a --arguments    "
        "      Arguments passed to script\n"
        "    -t --test         "
        "      Run unittest on current installation\n"
        "    -v --version      "
        "      Print version")

def print_version() -> None:
    """Print nemoa version to standard output."""
    version = env.get_var('version') or ''
    ui.info('nemoa ' + version)

def print_workspaces() -> None:
    """Print list of workspaces to standard output."""
    nemoa.set('mode', 'silent')
    workspaces = nemoa.list('workspaces', base='user')
    ui.info('Workspaces:\n')
    for workspace in workspaces:
        ui.info('    %s' % (workspace))
    ui.info('')

def run_script(workspace: str, script: str, *args: Any) -> bool:
    """Run nemoa python script."""
    return nemoa.open(workspace) and nemoa.run(script, *args)

def run_shell() -> None:
    """Start nemoa session in IPython interactive shell."""
    name = env.get_var('name') or ''
    version = env.get_var('version') or ''
    banner = name + ' ' +  version
    shell.run(banner=banner)

def run_unittest() -> None:
    """Run unittest."""
    ui.info(f"testing nemoa {env.get_var('version')}")
    cur_level = ui.get_notification_level()
    ui.set_notification_level('CRITICAL')
    try:
        nemoa.test.run(stream=sys.stderr)
    finally:
        ui.set_notification_level(cur_level)

def main() -> Any:
    """Launch nemoa."""
    argv = sys.argv[1:]
    if not argv:
        return run_shell()

    # Get command line options
    shortopts = "hvtslw:s:a:"
    longopts = ["workspace=", "script=", "arguments="]
    try:
        opts, args = getopt.getopt(argv, shortopts, longopts)
    except getopt.GetoptError:
        return print_usage()

    dic = dict(opts)
    keys = dic.keys()
    given: Callable[..., bool] = (lambda *args: not keys.isdisjoint(set(args)))

    if given('-h', '--help'):
        return print_usage()
    if given('-v', '--version'):
        return print_version()
    if given('-t', '--test'):
        return run_unittest()
    if given('-s', '--shell'):
        return run_shell()
    if given('-l', '--list'):
        return print_workspaces()

    workspace = dic.get('-w') or dic.get('--workspace')
    if not workspace:
        return print_workspaces()
    script = dic.get('-r') or dic.get('--run-script')
    if not script:
        return print_scripts(workspace)
    arguments = dic.get('-a') or dic.get('--arguments')
    if not arguments:
        return run_script(workspace, script)
    return run_script(workspace, script, arguments)

if __name__ == "__main__":
    main()
