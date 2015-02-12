#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
curpath = os.path.abspath(os.path.dirname(__file__))
libpath = curpath + os.path.sep + 'lib'
import sys
sys.path.append(libpath)
import nemoa
import getopt

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
    workspaces = nemoa.list()
    print 'Workspaces:\n'
    for workspace in workspaces: print '    %s' % (workspace)
    print

def print_scripts(workspace):
    """Print list of scripts to standard output."""
    nemoa.log('set', mode = 'silent')
    workspace = nemoa.open(workspace)
    name = workspace.name
    scriptlist = workspace.list(type = 'script')
    scripts = [script['name'] for script in scriptlist]
    print 'Scripts in workspace %s:\n' % (name)
    for script in scripts: print '    %s' % (script)
    print

def execute(workspace, script, *args):
    nemoa.open(workspace).execute(script, *args)

def interactive():
    try:
        import IPython
        os.system('cls' if os.name=='nt' else 'clear')
        nemoa.log('set', mode = 'shell')
        IPython.embed(banner1 = 'nemoa ' + nemoa.version() + '\n')
    except:
        nemoa.log('error',
            """could not start interactive nemoa shell:
            you have to install ipython.""")

def version():
    print 'nemoa ' + nemoa.version()

def usage():
    """Print script usage to standard output."""
    print """Usage: %s [-w <workspace> [-s <script> [-a <arguments>]]] [-h] [-i] [-l] [-v]

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
