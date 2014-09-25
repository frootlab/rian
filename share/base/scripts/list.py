#!/usr/bin/env python

def main(workspace, **kwargs):
    name = workspace.name()
    content = workspace.list(namespace = name)
    print "Content of workspace %s:" % (name)
    for entry in content: print entry
