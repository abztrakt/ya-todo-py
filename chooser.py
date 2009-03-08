#!/usr/bin/env python
"""
chooser.py - a parsescript for todo.py
    Takes in a file path or URL.
"""

__author__  = "Craig M. Stimmel"
__license__ = "GPL"

import sys
import subprocess
import getopt
import openanything

EDITOR = "vim"

def getFile(filepath):
    """ Use openanything to open a file or url and return a dictionary of info about it """
    file = openanything.fetch(filepath)
    return file

def parseFile(file):
    """ Process the text and return todo items that can be written to the todo.txt data file """
    # Create a tempfile and write our data into it
    tempfile = "/tmp/todotemp.txt"
    thandle = open(tempfile, 'w')
    thandle.write(file['data'])
    thandle.close()

    # Open our tempfile and edit it
    edit = subprocess.call([EDITOR, tempfile])

    # Read the tempfile back in as todos
    thandle = open(tempfile, 'r')
    todos = thandle.read()
    thandle.close()
    return todos

def writeTodos():
    """ Write out the todo items into the todo.txt storage """
    pass

def main(filepath):
    file = getFile(filepath)
    print parseFile(file)

if __name__ == "__main__":
    filepath = sys.argv[1]
    main(filepath)
