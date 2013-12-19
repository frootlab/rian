#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('./package')
import nemoa, getopt, os

def main(argv):

    project = ''
    script  = ''
    kwargs  = ''

    # get arguments
    try: opts, args = getopt.getopt(argv, "hvp:s:a:",
        ["project=", "script=", "arguments="])
    except getopt.GetoptError: usage(); sys.exit(2)

    # parse arguments
    for opt, arg in opts:
        if opt == '-h': usage(); sys.exit()
        elif opt == '-v': version(); sys.exit()
        elif opt in ("-p", "--project"):   project = arg
        elif opt in ("-s", "--script"):    script = arg
        elif opt in ("-a", "--arguments"): kwargs = arg

    # do something
    if not project: usage(); projects(); sys.exit()
    if not script: usage(); scripts(project); sys.exit()
    execute(project, script, kwargs)

def projects():
    """Print list of projects to standard output."""
    print 'Projects: ' + ','.join(['%s' % (p) for p in nemoa.listProjects()])

def scripts(project):
    """Print list of scripts to standard output."""
    nemoa.setLog(quiet = True)
    workspace = nemoa.open(project)
    nemoa.setLog(quiet = False)
    scripts = workspace.list(type = 'script', namespace = workspace.project())
    print 'Scripts in project %s:\n' % (project)
    for script in scripts:
        print '    %s' % (script)
    print ''

def execute(project, script, kwargs):
    workspace = nemoa.open(project)
    workspace.execute(name = script, arguments = kwargs)

def version(): print nemoa.version()

def usage():
    """Print script usage to standard output."""
    print """Usage: %s [-p <project> [-s <script> [-a <arguments>]]] [-h] [-v]
    
    -h --help                 Print this
    -p --project              User Namespace / Project
    -s --script               Basename of script to execute
    -a --arguments            Arguments passed to script
    -v --version              Print version
    """ % (os.path.basename(__file__))

if __name__ == "__main__":
   main(sys.argv[1:])
