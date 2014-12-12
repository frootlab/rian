#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt
import os
from subprocess import call

sys.path.append('./package')
import nemoa

def main(argv):

    workspace = ''
    script = ''
    kwargs = ''
    ipython = False

    # get arguments
    try: opts, args = getopt.getopt(argv, "hvilw:s:a:",
        ["workspace=", "script=", "arguments="])
    except getopt.GetoptError: usage(); sys.exit(2)

    if len(opts) == 0: usage(); sys.exit()

    # parse arguments
    for opt, arg in opts:
        if opt in ['-h', '--help']: usage(); sys.exit()
        elif opt in ['-v', '--version']: version(); sys.exit()
        elif opt in ['-i', '--interactive']: interactive(); sys.exit()
        elif opt in ['-l', '--list']: print_workspaces(); sys.exit()
        elif opt in ['-w', '--workspace']: workspace = arg
        elif opt in ['-s', '--script']: script = arg
        elif opt in ['-a', '--arguments']: kwargs = arg

    # do something
    if not workspace: usage(); print_workspaces(); sys.exit()
    if not script: usage(); print_scripts(workspace); sys.exit()
    execute(workspace, script, kwargs)

def print_workspaces():
    """Print list of workspaces to standard output."""
    nemoa.log('set', mode = 'silent')
    workspaces = nemoa.workspaces()
    print 'Workspaces:\n'
    for workspace in workspaces: print '    %s' % (workspace)
    print

def print_scripts(workspace):
    """Print list of scripts to standard output."""
    nemoa.log('set', mode = 'silent')
    workspace = nemoa.open(workspace)
    name = workspace.name()
    scripts = workspace.list(type = 'script', workspace = name)
    print 'Scripts in workspace %s:\n' % (name)
    for script in scripts: print '    %s' % (script)
    print

def execute(workspace, script, kwargs):
    nemoa.welcome()
    nemoa.open(workspace).execute(name = script, arguments = kwargs)

def interactive():
    try:
        call(['ipython', 'nemoa.interactive.py', '-i'])
    except:
        nemoa.log('error',
            """could not start interactive nemoa shell:
            you have to install ipython.""")

def version(): print nemoa.version()

def usage():
    """Print script usage to standard output."""
    print """Usage: %s [-w <workspace> [-s <script> [-a <arguments>]]] [-h] [-v]

    -h --help                 Print this
    -i --interactive          Start nemoa in iPython interactive shell
    -l --list                 List workspaces
    -w --workspace            List scripts in workspace
    -s --script               Open workspace and execute script
    -a --arguments            Arguments passed to script
    -v --version              Print version
    """ % (os.path.basename(__file__))

if __name__ == "__main__":
   main(sys.argv[1:])
