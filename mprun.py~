#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt, os

def main(argv):
    project = ''
    script = ''
    kwargs = ''
    params = {}

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

    if not project or not script:
        usage()
        sys.exit()

    # create workspace and open project
    sys.path.append('./package')
    import metapath
    workspace = metapath.open(project)

    # execute python script
    workspace.execute(
        name = script,
        params = params,
        arguments = kwargs)

def usage():
    """Print script usage"""

    print """Usage: mprun.py -p <project> -s <script> [-a <arguments>]
    
    -h --help                 Prints this
    -p --project              User Namespace / Project
    -s --script               Basename of script to execute
    -a --arguments            Arguments passed to script
    """

if __name__ == "__main__":
   main(sys.argv[1:])
