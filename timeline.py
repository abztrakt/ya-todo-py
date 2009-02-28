#!/usr/bin/python

""" TODO.TXT Timeline View Reporter
Based on bidseye.py by Gina Trapani
USAGE:  
    timeline.py [todo.txt]
    
USAGE NOTES:
    Expects a text file as parameter, formatted as follows:
    - One todo per line, ie, "My big project {start: 2006-12-27} {due: 2006-12-30}"
    - with starting and due dates as extensions: {start: 2006-12-27} {due: 2006-12-30}
    - any todo without start and end dates is simply not included in the timeline
    
    See more on todo.txt here:
    http://todotxt.com
    
    
OUTPUT:
    Displays a timeline of projects that have start and due dates defined:
        hw 1 +class1              12/22 |++++++++!| 12/29
        hw 2 +class2              12/25    |+++++*-| 12/31
        program design +class3    12/26     |+++!!| 12/28
        program complete +class3  12/26     |++++*---------| 01/08
        hw 2 +class1              12/29        |+*------| 01/05
        hw 1 +class4              12/30         |*----| 01/03
        
    Today is represented by *, late days are !s.
    

CHANGELOG:
    2006.12.30 - Started: translated the original awk version to python and
                 fit into a birdseye style framework.
"""


import sys
import os
import datetime
import time
from datetime import date
import re

__version__ = "1.0"
__date__ = "2006/12/30"
__updated__ = "2006/12/30"
__author__ = "Alex Weiss <algrs@cacography.net>, based on work by Gina Trapani (ginatrapani@gmail.com)"
__copyright__ = "Copyright 2006, Alex Weiss, Gina Trapani"
__license__ = "GPL"
__history__ = """
1.0 - Released.
"""

def getDict(file=""):
    if file == "":
        if os.environ.has_key("TODO_DIR"):
            dir = os.environ["TODO_DIR"]
        if os.name == 'nt':
            if not dir: dir = os.path.expanduser(r"~\My Documents")
        if not dir: dir = os.path.expanduser("~/todo")
        if os.path.isdir(dir):
            file = dir + os.path.sep + "todo.txt"
        else:
            usage()
            sys.exit(2)
        
    """a utility method to obtain a dictionary of tasks from a file"""
    count = 0
    tasks = {}
    # build a dictionary of the todo list items
    try:
        for line in open(file).readlines():
            if (line.strip() == ""): continue
            count = count + 1
            tasks[count] = line.rstrip()
        return tasks
    except (IOError, os.error), why:
        return {}



def usage():
    print "USAGE:  %s [todo.txt]"% (sys.argv[0], )

def conditional(b, rt, rf):
    if b:
        return rt
    else:
        return rf

def main(argv):
    if len(argv) < 1:
        tasks = getDict()
    else:
        tasks = getDict(argv[0])
    rightnow = date(*time.localtime()[0:3])
    re_duedate = re.compile(r"(.*)\{due: (....)-(..)-(..)[^\}]*\}(.*)")
    re_startdate = re.compile(r"(.*)\{start: (....)-(..)-(..)[^\}]*\}(.*)")
    
    pending = []
    
    for k,v in tasks.iteritems():
        matches = re_duedate.search(v)
        if matches != None:
            item = matches.group(1) + matches.group(5)
            due = date(int(matches.group(2)), int(matches.group(3)), int(matches.group(4)))
        else:
            continue
        matches = re_startdate.search(item)
        if matches != None:
            item = matches.group(1) + matches.group(5)
            begin = date(int(matches.group(2)), int(matches.group(3)), int(matches.group(4)))
        else:
            continue
        if begin <= rightnow:
            pending.append([item, begin, due])
    pending.sort(lambda x,y: cmp(x[1],y[1]))
    maxlength = 0
    for p in pending:
        if len(p[0]) > maxlength: maxlength = len(p[0])
    if len(pending) > 0:
        firststart = pending[0][1]
        for p in pending:
            print "%s %s %s %s" \
                % (p[0] + (maxlength - len(p[0])) * " ",\
                p[1].strftime("%m/%d"),\
                (p[1] - firststart).days * " " \
                + "|" \
                + (min(rightnow, p[2]) - p[1]).days * "+" \
                + conditional(rightnow <= p[2], "*", "+") \
                + (p[2] - rightnow).days * "-" \
                + (rightnow - p[2]).days * "!" \
                + "|" ,\
                p[2].strftime("%m/%d"))

if __name__ == "__main__":
    main(sys.argv[1:])
