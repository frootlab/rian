#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

def main():
    """ """
    import getopt
    import sys

    argv = sys.argv[1:]

    def print_scripts(workspace):
        """Print list of scripts to standard output."""
        import nemoa

        nemoa.set('mode', 'silent')
        if not nemoa.open(workspace):
            return False
        print(('Scripts in workspace %s:\n' % (nemoa.get('workspace'))))
        for script in nemoa.list('scripts'):
            print(('    %s' % (script)))
        print()

        return True

    def print_usage():
        """Print script usage to standard output."""
        print("Usage: nemoa [options]\n\n"
            "Options:\n\n"
            "    -h --help         "
            "      Print this\n"
            "    -g --gui          "
            "      Start nemoa QT user interface\n"
            "    -i --interactive  "
            "      Start nemoa interactive shell\n"
            "    -l --list         "
            "      List workspaces\n"
            "    -w --workspace    "
            "      List scripts in workspace\n"
            "    -s --script       "
            "      Open workspace and execute script\n"
            "    -a --arguments    "
            "      Arguments passed to script\n"
            "    -t --test         "
            "      Run unittest on current installation\n"
            "    -v --version      "
            "      Print version")

        return True

    def print_version():
        """Print nemoa version to standard output."""
        import nemoa
        print(('nemoa ' + nemoa.__version__))
        return True

    def print_workspaces():
        """Print list of workspaces to standard output."""
        import nemoa

        nemoa.set('mode', 'silent')
        workspaces = nemoa.list('workspaces', base='user')
        print('Workspaces:\n')
        for workspace in workspaces:
            print(('    %s' % (workspace)))
        print()

        return True

    def run_gui():
        """Run nemoa qt user interface."""
        import nemoa

        try:
            import nemoagui
        except ImportError:
            raise Warning('nemoagui is not installed.')

        return nemoagui.start()

    def run_script(workspace, script, *args):
        """Run nemoa python script."""
        import nemoa

        return nemoa.open(workspace) and nemoa.run(script, *args)

    def run_shell():
        """Run nemoa interactive shell."""
        from nemoa.session.console import shell

        return shell.main()

    def run_unittest() -> None:
        """Run unittest."""
        from nemoa.core import napp, test

        print(f"testing nemoa {napp.get_var('version')}")
        test.run_tests(stream=sys.stderr)

    workspace = ''
    script = ''
    arguments = ''
    mode = 'script'

    # get arguments
    try:
        opts, args = getopt.getopt(argv, "hgvtilw:s:a:",
            ["workspace=", "script=", "arguments="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    if not opts:
        print_usage()
        sys.exit()

    # parse arguments and set mode
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            mode = 'showhelp'
        elif opt in ['-v', '--version']:
            mode = 'showversion'
        elif opt in ['-t', '--test']:
            mode = 'test'
        elif opt in ['-i', '--interactive']:
            mode = 'shell'
        elif opt in ['-l', '--list']:
            mode = 'showworkspaces'
        elif opt in ['-g', '--gui']:
            mode = 'gui'
        elif opt in ['-w', '--workspace']:
            workspace = arg
        elif opt in ['-s', '--script']:
            script = arg
        elif opt in ['-a', '--arguments']:
            arguments = arg

    if mode == 'showhelp':
        print_usage()
    elif mode == 'showversion':
        print_version()
    elif mode == 'showworkspaces':
        print_workspaces()
    elif mode == 'shell':
        run_shell()
    elif mode == 'gui':
        run_gui()
    elif mode == 'test':
        run_unittest()
    elif mode == 'script':
        if not workspace:
            print_usage()
            print_workspaces()
        elif not script:
            print_usage()
            print_scripts(workspace)
        else:
            if arguments:
                run_script(workspace, script, arguments)
            else:
                run_script(workspace, script)

if __name__ == "__main__":
    main()
