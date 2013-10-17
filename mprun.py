#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt, os

def main(argv):
    project = ''
    script = ''
    params = {}

    try:
        opts, args = getopt.getopt(argv,"hp:s:",["project=", "script="])
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

    if not project or not script:
        usage()
        sys.exit()

    ## create workspace and open project
    sys.path.append('./package')
    import metapath
    workspace = metapath.open(project)
    workspace.execute(name = script, params = params)

def usage():
    print """Usage: mprun.py -p <project> -s <script>
    
    -h --help                 Prints this
    -p --project              Execute a metapath script
    -s --script               Print dothis
    -a --argument (argument)  Print (argument)
    """

if __name__ == "__main__":
   main(sys.argv[1:])
