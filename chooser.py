#!/usr/bin/env python
"""
chooser.py - a parsescript for todo.py
    Takes in a file path or URL.
"""

__author__  = "Craig M. Stimmel"
__license__ = "GPL"

import sys
import os
import subprocess
import tempfile
import getopt
import openanything
import todo

# Where are our todos stored?
if todo.TODO_DIR:
    todo_dir = todo.TODO_DIR
else:
    try:
        todo_dir = "%s/todo/" % os.environ['HOME']
    except:
        print "Your todo directory cannot be found!"

# Figure out what editor to use, if not that, default to vi
try:
    if(os.environ['TODO_EDITOR']):
        editor = os.environ['TODO_EDITOR']
    else:
        editor = os.environ['EDITOR']
except:
    editor = 'vi'

def getFile(source):
    """ Use openanything to open a file or url and return a dictionary of info about it """
    file = openanything.fetch(source)
    return file

def parseFile(file):
    """ Process the text and return todo items that can be written to the todo.txt data file """
    # Create a tempfile and write our data into it
    tfile = tempfile.mkstemp()[1]
    thandle = open(tfile, 'w')
    thandle.write(file['data'])
    thandle.close()

    # Open our tempfile and edit it
    edit = subprocess.call([editor, tfile])

    # Read the tempfile back in as todos
    thandle = open(tfile, 'r')
    todos = thandle.read()
    thandle.close()

    # Clean up the tempfile, since mkstemp doesn't do that for us.
    cleanup = subprocess.Popen("rm " + tfile, shell=True)
    sts = os.waitpid(cleanup.pid, 0)

    return todos

def writeTodos(todos):
    """ Write out the todo items into the todo.txt storage """
    fhandle = open(todo_dir+'todo.txt', 'a')
    fhandle.write(todos)
    fhandle.close()

def main(source):
    file = getFile(source)
    todos = parseFile(file)
    writeTodos(todos)

if __name__ == "__main__":
    source = sys.argv[1]
    main(source)
