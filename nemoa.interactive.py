#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('./package')

import os
import nemoa

def main(argv):
    os.system('cls' if os.name=='nt' else 'clear')
    nemoa.log('set', mode = 'shell')
    nemoa.welcome()

if __name__ == "__main__":
    main(sys.argv[1:])
