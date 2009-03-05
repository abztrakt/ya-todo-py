#!/usr/bin/env python
"""
chooser.py - a parsescript for todo.py
    Takes in a file path or URL.
"""

__date__    = "2009/03/05"
__author__  = "Craig M. Stimmel"
__license__ = "GPL"

import sys
import getopt
import openanything

def getFile(filepath):
    """ Use openanything to open a file or url and return a dictionary of info about it """
    file = openanything.fetch(filepath)
    return file

def parseFile():
    """ Process the text and return todo items that can be written to the todo.txt data file """
    pass

def writeTodos():
    """ Write out the todo items into the todo.txt storage """
    pass

def main(filepath):
    file = getFile(filepath)
    print file["data"]

if __name__ == "__main__":
    filepath = sys.argv[1]
    main(filepath)
