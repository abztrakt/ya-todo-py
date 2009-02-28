#!/usr/bin/env python
"""
TODO.TXT Manager - Python Version
Author          : Shane Koster <shane.koster@gmail.com>
Modified by     : Graham Davies <grahamdaviez@gmail.com>
Concept by      : Gina Trapani (ginatrapani@gmail.com
License         : GPL, http://www.gnu.org/copyleft/gpl.html
More info       : http://todotxt.com
Project Page    : http://code.google.com/p/todotxt
Direct link     : http://todotxt.googlecode.com/svn/trunk/todo.py
Project todo.txt: http://todotxt.googlecode.com/svn/trunk/todo.txt
"""

__version__   = "1.8.1-py-beta"
__revision__  = "$Revision: 217 $"
__date__      = "2006/07/29"
__author__    = "Shane Koster (shane.koster@gmail.com)"
__copyright__ = "Copyright 2006, Gina Trapani"
__license__   = "GPL"
__history__   = "See http://todotxt.googlecode.com/svn/trunk/CHANGELOG"

# Set the full path to your TODO directory here
# leave blank to use default ~/todo or ~\My Documents directories
# For *nix use / dir separators, Windows use raw strings: eg. r"c:\dir"
# Or set this using the --todo-dir '/home/user/todo' format
TODO_DIR = ''

# Set default color theme
# ANSI (light|dark|nocolor) or Windows Console (windark)
# Or use -t theme flag
# Or use BGCOL environment variable
defaultTheme = 'light'

# Set default verbosity level with False or True
# True will display various messages after each action - useful for bots
# Or use -v flag
verbose = False
quiet = False
force = False

# should we wait for the editor to finish - or return to the shell now
# use waitEditor = True for console editors vim|vi|emacs|joe etc
# use False for notepad.exe|gedit|kedit 
waitEditor = True

# set your sort preferences
# Or use -i flag for sortIgnoreCase = False
# Or use -n flag for numericSort = True
sortIgnoreCase = True
# This default is used for ls action which can use alphaSort
numericSort = False

# Set your preferences, how entering priorities should be handled.
# singleLetterPriority = False means, you enter a priority of a
# task like this:
#   todo.py add [A] my important task or
#   todo.py add {A} my important task or
#   todo.py add "(A) my important task"
# This is the behavior as you know it from todo.py
#
# singleLetterPriority = True means, that you additionally can
# enter your priority as a single capital letter at the beginning
# of your todo like this:
#   todo.py add A this is my highest priority
# This todo will automatically converted to:
#   (A) this is my highest priority
#
singleLetterPriority = False

# Change default display for lsr, lsk, lsc (table|simple)
# simple shows only the project or context keyword
# table displays a table of counts, % and keywords similar to birdseye.py
displayType = 'table'

# ANSI Colors
NONE         = ""
BLACK        = "\033[0;30m"
RED          = "\033[0;31m"
GREEN        = "\033[0;32m"
BROWN        = "\033[0;33m"
BLUE         = "\033[0;34m"
PURPLE       = "\033[0;35m"
CYAN         = "\033[0;36m"
LIGHT_GREY   = "\033[0;37m"
DARK_GREY    = "\033[1;30m"
LIGHT_RED    = "\033[1;31m"
LIGHT_GREEN  = "\033[1;32m"
YELLOW       = "\033[1;33m"
LIGHT_BLUE   = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN   = "\033[1;36m"
WHITE        = "\033[1;37m"
DEFAULT      = "\033[0m"

# Windows Colors
WIN_BLACK    = 0x00
WIN_BLUE     = 0x01
WIN_GREEN    = 0x02
WIN_LBLUE    = 0x03
WIN_RED      = 0x04
WIN_PURPLE   = 0x05
WIN_YELLOW   = 0x06
WIN_WHITE    = 0x07
WIN_GREY     = 0x08

############################################################
# Be careful changing things below here

import re, os, sys, time, getopt, sets
from shutil import copyfile
import datetime
import time
from datetime import date


def usage():
    text =  "Usage: todo.py [options] [ACTION] [PARAM...] \n"
    text += "Try `todo.py -h' for more information."
    print text

def help(longmessage = False):
    if longmessage:
        print __doc__
        text = "  Usage: " + sys.argv[0] + """ [options] [ACTION] [PARAM...]

  Actions:
    add [PRIORITY] "p:project @context THING I NEED TO DO"
    a   [PRIORITY] "p:project @context THING I NEED TO DO"
      Adds TODO ITEM to your todo.txt.
      Project and context notation optional.
      Quotes optional except when text includes any of !#()$&*\|;<>`~
      Optional priority can be added with [a], {a} or "(a)"
      PRIORITY must be a letter between A and Z, case insensitive.

    done "THING I HAVE DONE p:project @context"
      Add DONE ITEM to your done.txt.
      Project and context notation optional
      Quotes optional.

    append NUMBER "TEXT TO APPEND"
      Adds TEXT TO APPEND to the end of the todo on line NUMBER.
      Quotes optional.

    prepend NUMBER "TEXT TO PREPEND"
    prep    NUMBER "TEXT TO PREPEND"
       Adds TEXT TO PREPEND to the beginning of the todo on line NUMBER.
       Quotes optional.

    archive
      Moves done items from todo.txt to done.txt.

    del NUMBER
    rm  NUMBER
      Deletes the item on line NUMBER in todo.txt.

    do NUMBER
    do NUMBER "TEXT TO ADD AS COMMENT"
      Marks item on line NUMBER as done in todo.txt.
      Optional comment can be added to end of todo appears as " # comment"

    doall NUMBER [NUMBER]...
    doa NUMBER [NUMBER]...
    da NUMBER [NUMBER]...
      Marks all items on lines NUMBER... as done in todo.txt.

    list [TERM] [[TERM]...]
    ls   [TERM] [[TERM]...]
      Displays all todo's that contain TERM(s) sorted by priority with line
      numbers.  If no TERM specified, lists entire todo.txt.

    listall [TERM...]
    lsa     [TERM...]
       Displays all the lines in todo.txt AND done.txt that contain TERM(s)
       sorted by priority with line  numbers.  If no TERM specified, lists
       entire todo.txt AND done.txt concatenated and sorted.

    lspri [PRIORITY]
    lsp   [PRIORITY]
      Displays all items prioritized PRIORITY.
      If no PRIORITY specified, lists all prioritized items.

    pri NUMBER PRIORITY
      Adds PRIORITY to todo on line NUMBER.  If the item is already
      prioritized, replaces current priority with new PRIORITY.
      PRIORITY must be a letter between A and Z.

    today [TERM...]
      Print tasks completed today that contain TERM

    week [TERM...]
      print tasks completed in the last 7 days that contain TERM

    edit
    e
      Opens your todo.txt file with $EDITOR or /etc/alternatives/editor.

    edone
    ed
      Opens your done.txt file with $EDITOR or /etc/alternatives/editor.

    erecur
    er
      Opens your recur.txt file with $EDITOR or /etc/alternatives/editor.

    replace NUMBER "UPDATED TODO"
      Replaces todo on line NUMBER with UPDATED TODO.

    remdup
      Removes exact duplicate lines from todo.txt.

    report
      Adds the number of open todo's and closed done's to report.txt.

    birdseye
    b
      Birdseye View Report. To use this, get birdseye.py from
      http://todo-py.googlecode.com/svn/trunk/birdseye.py

   extension NUMBER "TYPE" "VALUE"    
     Add extension {type:value} the end of the todo
     
   extension NUMBER "TYPE"             
     Remove extension {type:*} from the todo

   comment NUMBER "VALUE"           
     Add comment the end of the todo
     
   comment NUMBER                    
     Remove comment from the todo
   
   link NUMBER "VALUE"          
     Add link the end of the todo
   
   link NUMBER                   
     Remove link from the todo
   
   resource NUMBER "VALUE"           
     Add resource the end of the todo
   
   resource NUMBER                    
     Remove resource from the todo
   
   percentdone NUMBER PERCENT      
     Set percent done extension

   percentdone NUMBER       
     Remove percent done extension

   due NUMBER DATE      
     Set due date extension

   due NUMBER       
     Remove due date extension

   starts NUMBER DATE      
     Set start date extension

   starts NUMBER       
     Remove start date extension

   wait NUMBER "FOR"
     Set/remove waiting for

   t, timeline                     
     Show timeline view of all items with start & due dates


  Options:
    -nc, -p        : Turns off colors
    -V, --version  : prints version number
    -h, --help     : print help
    -n             : sort items by number not alphabeticaly
    -t, --theme    : color theme ANSI: light|dark|nocolor, Win: windark
    --todo-dir     : Specifiy full path to directory containing todo.txt etc
    -i             : Make sort case sensitive

  More on the todo.txt manager at
  http://todotxt.com
  Version """ + __version__ + " " + __revision__[1:-1] + """
  Copyleft 2006, Gina Trapani (ginatrapani@gmail.com)
  Copyleft 2006, Shane Koster (shane.koster@gmail.com)
"""
    else:

        text = "todo.txt manager " + __version__ + " " + __revision__[1:-1] + """
Copyleft 2006  Gina Trapani, Shane Koster

Usage: todo.py [options] [ACTION] [PARAM...]

 a,   add "TODO p:project @context"   Add TODO to your todo.txt
 ls,  list  [TERM] [[TERM]...]        Display todo's that contain TERM *
 lsn, listn [TERM] [[TERM]...]        Same as ls but with numeric sort
 lsp, lspri [PRIORITY]                Display all items prioritized PRIORITY
 lsc, [all]contexts                   Display contexts in todo.txt *
 lsr, [all]projects                   Display projects in todo.txt *
 lsk, [all]keywords                   Display projects and contexts  *
 p,   pri NUMBER PRIORITY             Set PRIORITY on todo NUMBER
      do NUMBER [COMMENT]             Mark item NUMBER as done
      done "DONE p:project @context"  Add DONE to your done.txt
      append NUMBER "TEXT"            Add to the end of the todo
      prepend NUMBER "TEXT"           Add to the beginning of the todo
 rm,  del NUMBER                      Delete item on todo NUMBER
      replace NUMBER "UPDATED TODO"   Replace todo NUMBER with UPDATED TODO
 e,   edit                            Opens todo.txt in $EDITOR
ed,   edone                           Opens done.txt in $EDITOR
er,   erecur                          Opens recur.txt in $EDITOR
      remdup                          Remove exact duplicate todo's
ar,   archive                         Move done items to done.txt
      report                          Add todo and done count to report.txt
 b,   birdseye                        Bird's eye view report
da,   doall NUMBER [NUMBER]...        Mark all items NUMBER as done
 y,   today [TERM...]                 Display tasks done today with TERM
 w,   week [TERM...]                  Display tasks in last 7 days with TERM
      extension NUM "TYPE" ["VALUE"]  Add/remove extension {type:value} the todo
      comment NUMBER ["VALUE"]        Add/remove comment the todo
      link NUMBER ["VALUE"]           Add/remove link the todo
      resource NUMBER ["VALUE"]       Add/remove resource the todo
      percentdone NUMBER [PERCENT]    Set/remove percent done extension
      due NUMBER [DATE]               Set/remove due date extension
      starts NUMBER [DATE]            Set/remove start date extension
      wait NUMBER "FOR"               Set/remove waiting for
 t,   timeline                        Show timeline view of items with start & due dates


Options:
 -p,  -nc       : Turns off colors
 -t, --theme    : Specify color theme ANSI: light|dark|nocolor, Win: windark
 -V,  --version : Print version number
 -n             : sort items by number not alphabeticaly
 -i             : Make sort case sensitive
 -a             : Display text from TODO and DONE
 --todo-dir     : Specifiy full path to directory containing todo.txt etc
 --help         : Full help
 * addition of a to abbreviated form displays done.txt also - eg. lsa, lsra

"""
    print text
    sys.exit()

def formatDate(datestring):
    if datestring.lower() in ["now","today"]:
        t = time.localtime()
    else:
        Parsed = False
        formats = ["%Y-%m-%d %H:%M","%m/%d/%Y %H:%M","%Y-%m-%d %H.%M",\
        "%m/%d/%Y %H.%M","%y-%m-%d","%m/%d/%y","%y-%m-%d %H:%M","%m/%d/%y %H:%M",\
        "%y-%m-%d %H.%M","%m/%d/%y %H.%M","%Y-%m-%d","%m/%d/%Y", "%m-%d", "%m/%d",\
        "%m-%d %H.%M", "%m/%d %H.%M","%m-%d %H:%M", "%m/%d %H:%M"]
        for f in formats:
            try:
                #print "try %s on %s" % (f, datestring)
                t = time.strptime(datestring, f)
                Parsed = True
                break
            except ValueError:
                continue
        if not Parsed:
            print "Can't parse that date, try year-month-day hour:minute"
            sys.exit(1)
    if t[0] == 1900:
        d = datetime.datetime(time.localtime().tm_year,*t[1:5])
    else:
        d = datetime.datetime(*t[0:5])
    dateformatstr = "%Y-%m-%d"
    if d.hour > 0 or d.minute > 0:
        dateformatstr = dateformatstr + " %H:%M"
    if d.tzinfo != None:
        dateformatstr = dateformatstr + " %Z"
    return d.strftime(dateformatstr)

def setDirs(dir):
    """Your todo/done/report.txt locations"""
    global TODO_DIR, TODO_FILE, DONE_FILE, REPORT_FILE, TODO_BACKUP, DONE_BACKUP, RECUR_FILE

    if os.environ.has_key("TODO_DIR"):
        dir = os.environ["TODO_DIR"]
    if os.name == 'nt':
        if not dir: dir = os.path.expanduser(r"~\My Documents")
    if not dir: dir = os.path.expanduser("~/todo")

    if not os.path.isdir(dir):
        print "Can't open todo directory: %s" % dir
        sys.exit()
    TODO_DIR    = dir
    TODO_FILE   = dir + os.path.sep + "todo.txt"
    DONE_FILE   = dir + os.path.sep + "done.txt"
    REPORT_FILE = dir + os.path.sep + "report.txt"
    TODO_BACKUP = dir + os.path.sep + "todo.bak"
    DONE_BACKUP = dir + os.path.sep + "done.bak"
    RECUR_FILE  = dir + os.path.sep + "recur.txt"
    return True

def setTheme(theme):
    """Set colors for use when printing text"""
    global PRI_A, PRI_B, PRI_C, PRI_X, DEFAULT, LATE

    # Set the theme from BGCOL environment variable
    # only set if not set by cmdline flag
    if not theme and os.environ.has_key('BGCOL'):
        if os.environ['BGCOL'] == 'light':
            theme = 'light'
        elif os.environ['BGCOL'] == 'dark':
            theme = 'dark'

    # If no theme from cmdline or environment then use default
    if not theme: theme = defaultTheme

    if theme == "light":
        PRI_A = RED
        PRI_B = GREEN
        PRI_C = LIGHT_BLUE
        PRI_X = PURPLE
        LATE  = LIGHT_RED
    elif theme == "dark":
        PRI_A = YELLOW
        PRI_B = LIGHT_GREEN
        PRI_C = LIGHT_PURPLE
        PRI_X = WHITE
        LATE  = LIGHT_RED
    elif theme == "windark" and os.name == 'nt':
        PRI_A = WIN_YELLOW
        PRI_B = WIN_GREEN
        PRI_C = WIN_LBLUE
        PRI_X = WIN_GREY
        DEFAULT = WIN_WHITE
        LATE  = WIN_RED
    else:
        PRI_A = NONE
        PRI_B = NONE
        PRI_C = NONE
        PRI_X = NONE
        DEFAULT = NONE
        LATE = NONE

def getDict(file):
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

def getTaskDict():
    """a utility method to obtain a dictionary of tasks from the TODO file"""
    return getDict(TODO_FILE)

def getDoneDict():
    """a utility method to obtain a dictionary of tasks from the DONE file"""
    return getDict(DONE_FILE)

def writeTasks(taskDict):
    """a utility method to write a dictionary of tasks to the TODO file"""
    keys = taskDict.keys()
    keys.sort()
    backup(TODO_FILE, TODO_BACKUP)
    f = open(TODO_FILE, "w")
    for key in keys:
        f.write(taskDict[key] + os.linesep)
    f.close()

def writeDone(doneDict):
    keys = doneDict.keys()
    keys.sort()
    backup(DONE_FILE, DONE_BACKUP)
    f = open(DONE_FILE, "w")
    for key in keys:
        f.write(doneDict[key] + os.linesep)
    f.close()

def add(text):
    """Add a new task to the TODO file"""
    text = setPriority(text)
    f = open(TODO_FILE, "a")
    f.write(text + os.linesep)
    f.close()
    if not quiet: print "Added: ", text

def setPriority(text):
    """Handle priority if exisiting in supplied text"""

    if singleLetterPriority:
        re_pri = re.compile(r"^[A-Z] ")
        if re.search(re_pri, text):
        # A single capital letter was found, convert it to a priority!
            newpriority = "(" + text[0] + ") "
            text = re.sub(re_pri, newpriority, text)
    re_pri = re.compile(r"^[\(\[\{]([a-zA-Z])[\]\}\)]") # [a] or {a} or ()
    prio = re.search(re_pri, text)
    if prio:
        newpriority = "(" + prio.group(1).upper() + ")"
        text = re.sub(re_pri, newpriority, text)
    return text

def append(item, text=""):
    """Append text to a given task"""
    tasks = getTaskDict()
    if (not tasks.has_key(item)):
        print "%d: No such todo." % item
        sys.exit(1)
    tasks[item] = " ".join([tasks[item], text])
    writeTasks(tasks)
    if not quiet: print "Append: ", text

def prepend(item, text=""):
    """Prepend text to a given task.
       Preserve a priority at the beginning of the line, if one exists."""
    tasks = getTaskDict()
    if (not tasks.has_key(item)):
        print "%d: No such todo." % item
        sys.exit(1)
    # handle priority, if existing
    re_pri = re.compile(r"^\([A-Z]\) ")
    prio = re.search(re_pri, tasks[item])
    if prio:
        tasks[item] = re.sub(re_pri, "", tasks[item])
        tasks[item] = " ".join([text, tasks[item]])
        tasks[item] = prio.group(0) + tasks[item]
    else:
        tasks[item] = " ".join([text, tasks[item]])
    writeTasks(tasks)
    if not quiet: print "Prepend: %d %s" % (item, tasks[item])

def archive():
    tasks = getTaskDict()
    done = getDoneDict()
    tasksCopy = tasks.copy()
    for k,v in tasks.iteritems():
        if v.startswith("x"):
            done[len(done) + 1] = tasksCopy.pop(k)
    writeDone(done)
    writeTasks(tasksCopy)
    if verbose: print "Archive done"

def delete(item):
    tasks = getTaskDict()
    if (not tasks.has_key(item)):
        print "%d: No such todo." % item
        sys.exit(1)
    deleted = tasks.pop(item)
    writeTasks(tasks)
    if not quiet: print "Deleted: ", deleted

def backup(orig, backup):
    """Make a copy of the file before writing data"""
    if not os.path.isfile(orig): return
    try:
       copyfile(orig, backup)
    except (IOError, os.error), why:
       print "Can't copy %s to %s: %s" % (orig, backup, str(why))
       sys.exit()

def do(items, comments=None):
    """Set status of all items in items list to DONE.
       Optional comments will be appended to the task line"""

    tasks = getTaskDict()
    for item in items:
        item = int(item)
        if (not tasks.has_key(item)):
            print "%d: No such todo." % item
            continue
        # done items shouldn't be done again
        if isDone(tasks[item]): continue
        re_pri = re.compile(r"^\([A-Z]\) ")
        tasks[item] = re.sub(re_pri, "", tasks[item])

        # add comment text if any
        if comments: 
            tasks[item] = addComment(tasks[item], comments)

        date = time.strftime("%Y-%m-%d", time.localtime())
        print "Done %d: %s" % (item, tasks[item])
        tasks[item] = " ".join(["x", date, tasks[item]])
    writeTasks(tasks)
    archive()

def addComment(text, comments):
    """Add a comment to the text of a task"""
    text = text + " # " + " ".join(comments)
    return text
 
def isDone(text):
    """Check if an item is a 'done' item"""
    if text.startswith("x "): 
        return True
    else: 
        return False


def done(item):
    """add a completed task directly to done file"""
    date = time.strftime("%Y-%m-%d", time.localtime())
    text = " ".join(["x", date, item])
    f = open(DONE_FILE, "a")
    f.write(text + os.linesep)
    f.close()
    if not quiet: print "Done: %s" % item

def list(patterns=None, escape=True, \
        listDone=False, matchAny=False, dates=None, remove=False, showExtensions=True):
    """ List todo items.

        patterns  - the pattern to search for in the TODO files.
        escape - switch, wether the pattern is provided by the
                    user and therefore has to be escaped.
        listDone   - switch, wether the list should show only the content
                    of the TODO file (listDone=False) or the contents
                    of the TODO and the DONE files (listDone=True)
        remove    - tasks matching pattern are to be removed
        matchAny  - switch, patterns are AND (False) or OR (True) matched
        dates     - list of date patterns for search OR matched
    """
    items = []
    temp = {}
    tasks = getTaskDict()

    if listDone:
        # Add done dictionary to existing tasks
        done  = getDoneDict()
        new = len(tasks)
        for i in xrange(len(done)):
            new += 1
            tasks[new] = done[i+1]

    if patterns: 
        tasks = findPatterns(tasks, patterns, escape=escape, matchAny=matchAny, remove=remove)

    if dates: tasks = addDates(tasks, dates)

    # Format gathered tasks
    for k,v in tasks.iteritems():
        items.append("%3d: %s" % (k, v))

    # Print this before the tasks to make jabber bot pretty
    if verbose:
        print "todo.py: %d tasks in %s:" % ( len(items), TODO_FILE )

    #items.sort() # sort by todo.txt order
    if (not numericSort):
        items.sort(alphaSort) # sort by tasks alphbetically

    re_pri = re.compile(r".*(\([A-Z]\)).*")
    re_late = re.compile(r"(.*)\{due: (....)-(..)-(..)\}(.*)")
    re_late2 = re.compile(r"(.*)\{due: (....)-(..)-(..) (..):(..)\}(.*)")
    re_anyext = re.compile(r"\{[^\}]*\}")
    for item in items:
        if not showExtensions:
            item = re_anyext.sub("", item)
        if os.name == "nt":
            print re_pri.sub(highlightWindows, item)
            set_wincolor(DEFAULT)
        elif theme == 'nocolor':
            print item
        else:
            print re_late2.sub(highlightLate2, (re_late.sub(highlightLate, re_pri.sub(highlightPriority, item))))

def findPatterns(tasks, patterns, escape=True, matchAny=False, remove=False):
    """Return a task list based on a pattern - use remove for negate"""
    temp = {}
    for k,v in tasks.iteritems():
        # Match any or all tasks using matchAny switch
        match = True
        if matchAny: match = False
        for pattern in patterns:
            if escape: pattern = re.escape(pattern)
            if matchAny:
                if (re.search(pattern, v, re.IGNORECASE)): match = True
            else:
                if (not re.search(pattern, v, re.IGNORECASE)): match = False

        if remove:
            # remove adds tasks if not matched
            if not match: temp[k] = v
        else:
            # remove=False add if matched
            if match: temp[k] = v
    return temp

def addPatterns(tasks, patterns, escape=True, matchAny=False):
    """Add tasks that match a list of patterns"""
    return findPatterns(tasks, patterns, escape=escape, matchAny=matchAny, remove=False)

def removePatterns(tasks, patterns, escape=True, matchAny=False):
    """Remove tasks that match a list of patterns"""
    return findPatterns(tasks, patterns, escape=escape, matchAny=matchAny, remove=True)

def hideInclude(tasks):
    """Remove #INCLUDE statements from task list"""
    patterns = ['#INCLUDE']
    return removePatterns(tasks, patterns, escape=False)

def addDates(tasks, dates):
    """Match tasks with a dates in a date list"""
    temp = {}
    for k,v in tasks.iteritems():
        match = False
        for date in dates:
            if (re.search(date, v, re.IGNORECASE)): match = True

        if (match == True): temp[k] = v
    return temp

def removeDone(tasks):
    """Remove done tasks from a task list"""
    temp = {}
    for k,v in tasks.iteritems():
        if isDone(v):
            temp[k] = v
    return temp

def listKeywords():
    """Preliminary function to count keywords in todo and done files"""
    items = []
    tasks = getTaskDict()
    numTasks = len(tasks)

    # Add done dictionary to existing tasks
    # Can this be cone with zip() ?
    done  = getDoneDict()
    new = len(tasks)
    for i in xrange(len(done)):
        new += 1
        tasks[new] = done[i+1]

    projects = {}
    contexts = {}

    for k,v in tasks.iteritems():
        priority = hasPriority(v)
        words = v.split()
        for word in words:
            if len(word) < 2: continue
            if word[0:2] in ["p:", "p-"] or word.startswith("+"):
                if not projects.has_key(word):
                    projects[word] = dict(ntask=0,ndone=0,tlist=[],dlist=[],priority=0)
                if k <= numTasks:
                    projects[word]['ntask'] += 1
                    projects[word]['tlist'].append(k)
                    if priority: projects[word]['priority'] += 1
                else:
                    projects[word]['ndone'] += 1
                    projects[word]['dlist'].append(k)

            if word[0:1] == "@":
                if not contexts.has_key(word):
                    contexts[word] = dict(ntask=0,ndone=0,tlist=[],dlist=[],priority=0)
                if k <= numTasks:
                    contexts[word]['ntask'] += 1
                    contexts[word]['tlist'].append(k)
                    if priority: contexts[word]['priority'] += 1
                else:
                    contexts[word]['ndone'] += 1
                    contexts[word]['dlist'].append(k)
    return projects, contexts


def displaySummary(dict, name, listDone, type):
    """text display of project and context names in simple or table format"""

    if type == 'simple':
        for p in dict:
        # If not listDone only display those with entries in todo list
            if not dict[p]['ntask'] and not listDone: continue
            print p

    elif type == 'table':

        print "%4s %4s %4s %4s %-20s %s" % ("Todo", "Done", "%Done", "#Pri",
                name, "[Todo task numbers]")
        tdone = 0
        ttodo = 0
        tword = 0
        tprio = 0

        keys = dict.keys()
        keys.sort()
        for p in keys:
            # If not listDone only display those with entries in todo list
            if not dict[p]['ntask'] and not listDone: continue
            wtotal = dict[p]['ntask'] + dict[p]['ndone']
            percentDone = float(dict[p]['ndone']) / wtotal * 100

            #print "%4d %4d %4d %4d  %-20s" % (dict[p]['ntask'], dict[p]['ndone'],
                    #percentDone, dict[p]['priority'], p), dict[p]['tlist']
            row = "%4d %4d %4d %4d  %-20s " % (dict[p]['ntask'], dict[p]['ndone'],
                    percentDone, dict[p]['priority'], p)
            if dict[p]['tlist']:
                row += "["
                for tnum in dict[p]['tlist']:
                    row += "%d " % tnum
                row = row.rstrip()
                row += "]"
            print row
            ttodo += dict[p]['ntask']
            tdone += dict[p]['ndone']
            tprio += dict[p]['priority']
            tword += 1
        totalPercent = 0
        if tdone and ttodo: totalPercent = tdone / (tdone + ttodo) * 100.0
        print "%4d %4d %4d %4d  %-20d Column Totals" % (ttodo, tdone, totalPercent, tprio, tword)

    else:
        print "Please set the display type to simple or table"

def replace(item, text):
    """replace text to a given task"""
    tasks = getTaskDict()
    if (not tasks.has_key(item)):
        print "%d: No such todo." % item
        sys.exit(1)
    text = setPriority(text)
    tasks[item] = text
    writeTasks(tasks)

def sendToPrinter():
    try:
        os.execvp("todo_print.sh", ["todo_print.sh"])
    except (IOError, os.error), why:
        print "Problem with your printer script: %s" % str(why)
        sys.exit()

def edit(file):
    """opens your todo.txt file with a local editor if found"""
    if os.environ.has_key('EDITOR'):
        editor = os.environ['EDITOR']
    elif os.name == 'posix':
        editor = "/etc/alternatives/editor"

    if not waitEditor:
        try:
            from subprocess import Popen
            retcode = Popen([editor, file])
        except (IOError, os.error), why:
            print "Problem with your editor %s: %s" % (editor, str(why))
            sys.exit()
    else:
        try:
            os.execvp(editor, [editor, file])
        except (IOError, os.error), why:
            print "Problem with your editor %s: %s" % (editor, str(why))
            sys.exit()

def removeDuplicates():
    """Removes duplicate lines in the TODO file"""
    taskCopy = getTaskDict()
    theSet = sets.Set(taskCopy.values())
    dupCount = len(taskCopy) - len(theSet)
    if dupCount > 0:
        print "Removing %d duplicates." % (dupCount)
        count = 0
        tasks = {}
        for k,v in taskCopy.iteritems():
            if v in theSet:
                count += 1
                tasks[ count ] = v
                theSet.remove(v)
        writeTasks(tasks)
    else:
        print "There are no duplicates to eliminate!"
    sys.exit()

def confirm():
    print "Are you sure? (y/N)"
    answer = sys.stdin.readline().strip()
    if answer == "y":
        return
    else:
        if verbose: print "You said: '%s' - nothing changed." % answer
        sys.exit()

def report():
    """report open and closed tasks - airchive first"""
    archive()

    active = getTaskDict()
    closed = getDoneDict()

    date = time.strftime("%Y-%m-%d-%T", time.localtime())
    f = open(REPORT_FILE, 'a')
    string = "%s %d %d" % (date, len(active), len(closed))
    f.write(string + os.linesep)
    f.close()

def birdseye():
    try:
        import birdseye
    except ImportError:
        print "birdseye.py not found. You may get it from:"
        print "http://todotxt.googlecode.com/svn/trunk/birdseye.py"
        sys.exit()
    archive()
    birdseye.main([TODO_FILE, DONE_FILE])

def timeline():
    try:
        import timeline
    except ImportError:
        print "timeline.py not found. You may get it from:"
        print "http://todo-py.googlecode.com/svn/trunk/timeline.py"
        sys.exit()
    archive()
    timeline.main([TODO_FILE])

def alphaSort(a, b):
    """sorting function to sort tasks alphabetically"""
    if sortIgnoreCase:
        if (a[5:].lower() > b[5:].lower()): return 1
        elif (a[5:].lower() < b[5:].lower()): return -1
        else: return 0
    else:
        if (a[5:] > b[5:]): return 1
        elif (a[5:] < b[5:]): return -1
        else: return 0

def highlightWindows(matchobj):
    """color replacement function used when highlighting priorities"""
    if (matchobj.group(1) == "(A)"):
        set_wincolor(PRI_A)
    elif (matchobj.group(1) == "(B)"):
        set_wincolor(PRI_B)
    elif (matchobj.group(1) == "(C)"):
        set_wincolor(PRI_C)
    else:
        set_wincolor(PRI_X)
    return matchobj.group(0)

def highlightPriority(matchobj):
    """color replacement function used when highlighting priorities"""
    if (matchobj.group(1) == "(A)"):
        return PRI_A + matchobj.group(0) + DEFAULT
    elif (matchobj.group(1) == "(B)"):
        return PRI_B + matchobj.group(0) + DEFAULT
    elif (matchobj.group(1) == "(C)"):
        return PRI_C + matchobj.group(0) + DEFAULT
    else:
        return PRI_X + matchobj.group(0) + DEFAULT
        
def highlightLate(matchobj):
    """color replacement function used when highlighting overdue items"""
    due = date(int(matchobj.group(2)), int(matchobj.group(3)), int(matchobj.group(4)))
    if due <= date.today():
        return matchobj.group(1) + LATE + "{due: " + matchobj.group(2) + "-" + matchobj.group(3) + "-" \
        	+ matchobj.group(4) + "}" + DEFAULT + matchobj.group(5)
    else:
        return DEFAULT + matchobj.group(0) + DEFAULT

def highlightLate2(matchobj):
    """color replacement function used when highlighting overdue items with time"""
    due = datetime.datetime(int(matchobj.group(2)), int(matchobj.group(3)), int(matchobj.group(4)), \
    	int(matchobj.group(5)), int(matchobj.group(6)))
    if due <= datetime.datetime(*time.localtime()[0:5]):
        return matchobj.group(1) + LATE + "{due: " + matchobj.group(2) + "-" + matchobj.group(3) + "-" \
        	+ matchobj.group(4) + " " + matchobj.group(5) + ":" + matchobj.group(6) + "}" \
        	+ DEFAULT + matchobj.group(7)
    else:
        return DEFAULT + matchobj.group(0) + DEFAULT

def prioritize(item, newpriority):
    newpriority = newpriority.upper()
    tasks = getTaskDict()
    if (not tasks.has_key(item)):
        print "%d: No such todo." % item
        sys.exit(1)
    if (newpriority != "" and not re.match("[A-Z]", newpriority)):
        print "Priority not recognized: " + newpriority
        sys.exit(1)

    re_pri = re.compile(r"\([A-Z]\) ")

    if (newpriority == ""):
        # remove the existing priority
        tasks[item] = re.sub(re_pri, "", tasks[item])
    elif (re.match(re_pri, tasks[item])):
        tasks[item] = re.sub(re_pri, "(" + newpriority + ") ", tasks[item])
    else:
        tasks[item] = "(" + newpriority + ") " + tasks[item]

    writeTasks(tasks)

def hasPriority(text):
    re_pri = re.compile(r"^\(([A-Z])\) ")
    prio = re.search(re_pri, text)
    if prio:
        return prio.group(1)

def set_wincolor(color):
    """ set_wincolor(FOREGROUND_GREEN | FOREGROUND_INTENSITY)"""
    stdhandle = ctypes.windll.kernel32.GetStdHandle(-11)
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(stdhandle, color)
    return bool

def listDays(days=1):
    now = time.time()
    when = []
    for day in xrange(days):
        when.append(time.strftime("%Y-%m-%d", time.localtime(now)))
        now -= 86400
    list(args, escape=False, listDone=True, matchAny=True, dates=when)

def listItemNo(items):
    """List items by number"""
    tasks = getTaskDict()
    for item in items:
        if not item.isdigit(): 
            print "Error: '%s' is not a valid task number" % item
            sys.exit()
        item = int(item)
        if (not tasks.has_key(item)):
            print "%d: No such todo." % item
            continue
        print "%3d: %s" % (item, tasks[item])

def rmExtension(item, attribute):
    """remove an extension attribue"""
    tasks = getTaskDict()
    if (not tasks.has_key(item)):
        print "%d: No such todo." % item
        sys.exit(1)
    newitem = tasks[item]
    extstart = newitem.find(" {" + attribute)
    if extstart < 0:
        return
    extend = newitem.find("}", extstart+1)
    if extend < 0:
        return
    newitem = newitem[:extstart] + newitem[extend+1:]
    tasks[item] = newitem
    writeTasks(tasks)

def addExtension(item, attribute, value):
    """append an extension attribute"""
    #rmExtension(item, attribute)
    newextension = "{" + attribute + ": " + value + "}"
    append(item, newextension)


if __name__ == "__main__":

# Process command line arguments
    theme = None
    listDone = False


    try:
        opts, args = getopt.getopt(sys.argv[1:], 'fhpqvVint:d:', \
                ['nc', 'help', 'version','theme=','todo-dir=', 'type='])
    except (getopt.GetoptError), why:
        print "Sorry - option not recognized.  Try -h for help"
        sys.exit()

    for o, a in opts:
        if o == '-h':
            help()
        if o == '--help':
            help(longmessage=True)
        if o in ('-V', "--version"):
            print __version__, __revision__[1:-1]
            sys.exit()
        if o == '-v':
            verbose = True
        if o == '-q':
            """Quiet -- suppress printing of most information"""
            quiet = True
        if o == '-f':
            """Force feature not implemented - force by default now"""
            force = True
        if o == '-a':
            listDone = True
        if o == '-n':
            numericSort = True
        if o == '-i':
            sortIgnoreCase = False
        if o == '-d':
            """For backwards compatibility with todo.sh"""
        if o == '--todo-dir':
            """Specify TODO_DIR from command line"""
            TODO_DIR = a
        if o == '--type':
            """Specify display type for lsk, lsr, lsc etc"""
            displayType = a
        if o in ('-t', "--theme"):
            """Set the theme using -t theme flag"""
            theme = a
        if o in ('-p', '--nc'):
            theme = 'nocolor'

    if (len(args) < 1):
        """ Default action - should probably be help """
        action = 'list'
    elif args[0].isdigit():
        action = "listItemsByNumber"
    else:
        action = args[0]
        args   = args[1:]

# Set todo directory and all file names
    setDirs(TODO_DIR)

# Set the color theme
# Windows CMD themes require ctypes module only core > python 2.5
    if os.name == 'nt':
        if not theme in ['windark', 'nocolor']:
            theme = 'windark'
        try:
            import ctypes
        except ImportError:
            theme = 'nocolor'
    setTheme(theme)

# Collected arguments - ready to process actions
    if (action == "add" or action == "a"):
        if (args): add(" ".join(args))
        else:
            sys.stdout.write("Add? ")
            text = sys.stdin.readline().strip()
            add(text)
    elif (action == "append" or action == "app"):
        if (len(args) > 1 and args[0].isdigit()):
            append(int(args[0]), " ".join(args[1:]))
        else:
            help()
    elif (action == "prepend" or action == "prep"):
        if (len(args) > 1 and args[0].isdigit()):
            prepend(int(args[0]), " ".join(args[1:]))
        else:
            help()
    elif (action == "archive" or action == "ar"):
        archive()
    elif (action == "del" or action == "rm"):
        if (len(args) == 1 and args[0].isdigit()):
            #confirm()
            delete(int(args[0]))
        else:
            help()
    elif (action == "do"):
        if (args[0].isdigit()):
            do([args[0]],args[1:])
        else:
            help()
    elif (action == "doall" or action == "doa" or action == "da"):
        if (len(args) > 0):
            for a in args:
                if not a.isdigit():
                    print "Usage: " + sys.argv[0] + " doall <item_num> [item_num]..."
                    sys.exit()
            do(args)
        else:
            print "Usage: " + sys.argv[0] + " doall <item_num> [item_num]..."
    elif (action == "done"):
        if (args): done(" ".join(args))
        else:
            sys.stdout.write("Done? ")
            text = sys.stdin.readline().strip()
            done(text)
    elif (action == "ls" or action == "list"):
        if (action == "lsn" or action == "listn"): numericSort = True
        if (len(args) > 0):
            list(args, listDone=listDone)
        else:
            list(listDone=listDone)
    elif (action == "lsa" or action == "listall"):
        numericSort = False
        if (len(args) > 0):
            list(args, listDone=True)
        else:
            list(listDone=True)
    elif (action == "lsn" or action == "listnot"):
        numericSort = True
        if (len(args) > 0):
            list(args, listDone=False, matchAny=True, remove=True)
        else:
            list(listDone=False, matchAny=True, remove=True)
    elif (action == "lsp" or action == "lspri" or action == "listpri"):
        if (len(args) > 0):
            pattern = re.escape(args[0])
            x = ["\([" + pattern + "]\)"]
        else:
            x = ["\([A-Z]\)"]
        list(x, False)
    elif (action == "pri" or action == "p"):
        if (len(args) == 2 and args[0].isdigit() and args[1].isalpha()):
            prioritize(int(args[0]), args[1])
        elif (len(args) == 1 and args[0].isdigit()):
            # remove the existing priority
            prioritize(int(args[0]), "")
        else:
            print "Usage: " + sys.argv[0] + " pri <item_num> [PRIORITY]"
    elif (action == "replace"):
        if (len(args) > 1 and args[0].isdigit()):
            replace(int(args[0]), " ".join(args[1:]))
        else:
            print "Usage: " + sys.argv[0] + " replace <item_num> TEXT"
    elif (action == "edit" or action == "e"):
        edit(TODO_FILE)
    elif (action == "edone" or action == "ed"):
        edit(DONE_FILE)
    elif (action == "erecur" or action == "er"):
        edit(RECUR_FILE)
    elif (action == "remdup"):
        removeDuplicates()
    elif (action == "report"):
        report()
    elif (action == "today" or action == "y"):
        listDays(1)
    elif (action == "week" or action == "w"):
        listDays(7)
    elif (action in ["birdseye", "b", "bird", "summarize", "overview"]):
        birdseye()
    elif (action == "print"):
        sendToPrinter()
    elif (action in ["lsr", "listproj", "projects"]):
        projects, contexts = listKeywords()
        displaySummary(projects, name="Projects", listDone=False, type=displayType)
    elif (action in ["lsra", "listallproj", "allprojects"]):
        projects, contexts = listKeywords()
        displaySummary(projects, name="Projects", listDone=True, type=displayType)
    elif (action in ["lsc", "listcon", "contexts"]):
        projects, contexts = listKeywords()
        displaySummary(contexts, name="Contexts", listDone=False, type=displayType)
    elif (action in ["lsca", "listallcon", "allcontexts"]):
        projects, contexts = listKeywords()
        displaySummary(contexts, name="Contexts", listDone=True, type=displayType)
    elif (action in ["lsk", "listkeys", "keywords"]):
        projects, contexts = listKeywords()
        displaySummary(projects, name="Projects", listDone=False, type=displayType)
        displaySummary(contexts, name="Contexts", listDone=False, type=displayType)
    elif (action in ["lska", "listallkeys", "allkeywords"]):
        projects, contexts = listKeywords()
        displaySummary(projects, name="Projects", listDone=True, type=displayType)
        displaySummary(contexts, name="Contexts", listDone=True, type=displayType)
    elif (action == "listItemsByNumber"):
        listItemNo(args)
    elif (action == "extension"):
        if (len(args) > 2 and args[0].isdigit()):
            addExtension(int(args[0]), args[1], " ".join(args[2:]))
        elif (len(args) > 1 and args[0].isdigit()):
            rmExtension(int(args[0]), args[1])
        else:
            print "Usage: " + sys.argv[0] + " extension <item_num> TYPE [VALUE]"
    elif (action in ["comment", "link", "resource"]):
        if (len(args) > 1 and args[0].isdigit()):
            addExtension(int(args[0]), action, " ".join(args[1:]))
        elif (len(args) > 0 and args[0].isdigit()):
            rmExtension(int(args[0]), action)
        else:
            print "Usage: " + sys.argv[0] + " {comment,link,resource} <item_num> [VALUE]"
    elif (action == "percentdone"):
        if (len(args) > 1 and args[0].isdigit()):
            rmExtension(int(args[0]), "%done")
            addExtension(int(args[0]), "%done", args[1])
        elif (len(args) > 0 and args[0].isdigit()):
            rmExtension(int(args[0]), "%done")
        else:
            print "Usage: " + sys.argv[0] + " percentdone <item_num> [PERCENT]"
    elif (action == "due"):
        if (len(args) > 1 and args[0].isdigit()):
            rmExtension(int(args[0]), "due")
            addExtension(int(args[0]), "due", formatDate(" ".join(args[1:])))
        elif (len(args) > 0 and args[0].isdigit()):
            rmExtension(int(args[0]), "due")
        else:
            print "Usage: " + sys.argv[0] + " due <item_num> [DATE]"
    elif (action in ["starts","start"]):
        if (len(args) > 1 and args[0].isdigit()):
            rmExtension(int(args[0]), "start")
            addExtension(int(args[0]), "start", formatDate(" ".join(args[1:])))
        elif (len(args) > 0 and args[0].isdigit()):
            rmExtension(int(args[0]), "start")
        else:
            print "Usage: " + sys.argv[0] + " starts <item_num> [DATE]"
    elif (action == "wait"):
        if (len(args) > 1 and args[0].isdigit()):
            rmExtension(int(args[0]), "wait")
            addExtension(int(args[0]), "wait", " ".join(args[1:]))
        elif (len(args) > 0 and args[0].isdigit()):
            rmExtension(int(args[0]), "wait")
        else:
            print "Usage: " + sys.argv[0] + " wait <item_num> [for what]"
    elif (action == "timeline" or action == "t"):
        timeline()
    else:
        help()
