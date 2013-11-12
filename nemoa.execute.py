#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt, os

def main(argv):
    sys.path.append('./package')

    project = ''
    script = ''
    kwargs = ''


    try:
        opts, args = getopt.getopt(
            argv, "hvp:s:a:", ["project=", "script=", "arguments="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt == '-v':
            version()
            sys.exit()
        elif opt in ("-p", "--project"):
            project = arg
        elif opt in ("-s", "--script"):
            script = arg
        elif opt in ("-a", "--arguments"):
            kwargs = arg

    # print list of projects
    if not project:
        usage()
        listProjects()
        sys.exit()

    # print list of scripts in project
    if not script:
        usage()
        listScripts(project)
        sys.exit()

    # execute script
    executeScript(project, script, kwargs)

def listProjects():
    """Print list of projects to standard output."""
    import nemoa
    print 'Projects: ' + ','.join(['%s' % (p) for p in nemoa.listProjects()])

def listScripts(project):
    """Print list of scripts to standard output."""
    import nemoa
    nemoa.setLog(quiet = True)
    workspace = nemoa.open(project)
    nemoa.setLog(quiet = False)
    scripts = workspace.list(type = 'script', namespace = workspace.project())
    print 'Scripts in project %s:\n' % (project)
    for script in scripts:
        print '    %s' % (script)
    print ''

def executeScript(project, script, kwargs):
    import nemoa
    workspace = nemoa.open(project)
    workspace.execute(
        name = script,
        params = {},
        arguments = kwargs)

def version():
    import nemoa
    print nemoa.version()

def usage():
    """Print script usage to standard output."""
    
    script = os.path.basename(__file__)

    print """Usage: %s [-p <project> [-s <script> [-a <arguments>]]] [-h] [-v]
    
    -h --help                 Print this
    -p --project              User Namespace / Project
    -s --script               Basename of script to execute
    -a --arguments            Arguments passed to script
    -v --version              Print version
    """ % (script)

if __name__ == "__main__":
   main(sys.argv[1:])
