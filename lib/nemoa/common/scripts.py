#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def console():

    import getopt
    import sys

    argv = sys.argv[1:]

    def print_scripts(workspace):
        """Print list of scripts to standard output."""

        import nemoa

        nemoa.set('mode', 'silent')
        if not nemoa.open(workspace): return False
        print 'Scripts in workspace %s:\n' % (nemoa.get('workspace'))
        for script in nemoa.list('scripts'):
            print '    %s' % (script)
        print

        return True

    def print_usage():
        """Print script usage to standard output."""

        print """Usage: nemoa [-w <workspace> [-s <script> [-a <arguments>]]] [-h] [-i] [-l] [-v]

        -h --help                 Print this
        -i --interactive          Start nemoa in iPython interactive shell
        -l --list                 List workspaces
        -w --workspace            List scripts in workspace
        -s --script               Open workspace and execute script
        -a --arguments            Arguments passed to script
        -v --version              Print version
        """

        return True

    def print_version():
        """Print nemoa version to standard output."""

        import nemoa

        print 'nemoa ' + nemoa.__version__

        return True

    def print_workspaces():
        """Print list of workspaces to standard output."""

        import nemoa

        nemoa.set('mode', 'silent')
        workspaces = nemoa.list('workspaces', base = 'user')
        print 'Workspaces:\n'
        for workspace in workspaces: print '    %s' % (workspace)
        print

        return True

    def run_interactive():
        """Run nemoa in interactive ipython shell."""

        try:
            import IPython
        except ImportError:
            return nemoa.log('error',
                """could not start interactive nemoa shell:
                you have to install ipython.""")

        import nemoa
        import os

        os.system('cls' if os.name == 'nt' else 'clear')
        nemoa.set('mode', 'shell')
        IPython.embed(banner1 = 'nemoa %s\n' % nemoa.__version__)

        return True

    def run_script(workspace, script, *args):
        """Run nemoa python script in workspace."""

        import nemoa

        return nemoa.open(workspace) and nemoa.run(script, *args)

    workspace = ''
    script = ''
    arguments = ''
    mode = 'runscript'

    # get arguments
    try:
        opts, args = getopt.getopt(argv, "hvilw:s:a:",
            ["workspace=", "script=", "arguments="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    if len(opts) == 0:
        print_usage()
        sys.exit()

    # parse arguments and set mode
    for opt, arg in opts:
        if opt in ['-h', '--help']: mode = 'showhelp'
        elif opt in ['-v', '--version']: mode = 'showversion'
        elif opt in ['-i', '--interactive']: mode = 'runinteractive'
        elif opt in ['-l', '--list']: mode = 'showworkspaces'
        elif opt in ['-w', '--workspace']: workspace = arg
        elif opt in ['-s', '--script']: script = arg
        elif opt in ['-a', '--arguments']: arguments = arg

    if mode == 'showhelp': print_usage()
    elif mode == 'showversion': print_version()
    elif mode == 'showworkspaces': print_workspaces()
    elif mode == 'runinteractive': run_interactive()
    elif mode == 'runscript':
        if not workspace:
            print_usage()
            print_workspaces()
        elif not script:
            print_usage()
            print_scripts(workspace)
        else:
            if arguments: run_script(workspace, script, arguments)
            else: run_script(workspace, script)

if __name__ == "__main__":
   console()
