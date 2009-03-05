#!/usr/bin/env python
"""
chooser.py - a parsescript for todo.py
"""

__date__    = "2009/03/04"
__author__  = "Craig M. Stimmel"
__license__ = "GPL"

import sys
import getopt
import openanything

def getFile(filepath):
    file = openanything.fetch(filepath)
    return file

def parseFile():
    pass

def writeTodos():
    pass

def usage():
    pass

def main(filepath):
    file = getFile(filepath)
    print file["data"]

if __name__ == "__main__":
    filepath = sys.argv[1]
    main(filepath)
