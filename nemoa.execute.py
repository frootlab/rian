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
            argv, "hp:s:a:", ["project=", "script=", "arguments="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-p", "--project"):
            project = arg
        elif opt in ("-s", "--script"):
            script = arg
        elif opt in ("-a", "--arguments"):
            kwargs = arg

    if (script or kwargs) and not project:
        usage()
        sys.exit()

    # print list of projects
    if not project:
        if script or kwargs:
            usage()
            sys.exit()
        listProjects()
        sys.exit()

    # print list of scripts in project
    if not script:
        if kwargs:
            usage()
            sys.exit()
        listScripts(project)
        sys.exit()

    # execute script
    executeScript(project, script, kwargs)

def listProjects():
    """Print list of projects to standard output."""
    import nemoa
    nemoa.listProjects()

def listScripts(project):
    """Print list of scripts to standard output."""
    import nemoa
    nemoa.setLog(quiet = True)
    workspace = nemoa.open(project)
    nemoa.setLog(quiet = False)
    nemoa.log('title', 'scanning for scripts in project \'%s\'' % (project))
    nemoa.setLog(indent = '+1')
    workspace.list(type = 'script', namespace = workspace.project())
    nemoa.setLog(indent = '-1')

def executeScript(project, script, kwargs):
    params = {}
    import nemoa
    workspace = nemoa.open(project)
    workspace.execute(
        name = script,
        params = params,
        arguments = kwargs)

def usage():
    """Print script usage to standard output."""
    
    script = os.path.basename(__file__)

    print """Usage: %s [-p <project> [-s <script> [-a <arguments>]]] [-h]
    
    -h --help                 Print this
    -p --project              User Namespace / Project
    -s --script               Basename of script to execute
    -a --arguments            Arguments passed to script
    """ % (script)

if __name__ == "__main__":
   main(sys.argv[1:])
