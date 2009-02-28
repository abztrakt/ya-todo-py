#!/usr/bin/env python
"""
TODO.TXT Cron Helper
Author      : Graham Davies <grahamdaviez@gmail.com>
License     : GPL, http://www.gnu.org/copyleft/gpl.html
Project Page: http://code.google.com/p/todo-py
Direct link : http://todo-py.googlecode.com/svn/trunk/todo_cron.py
Modified    : 2007/07/22 Sean <schliden@gmail.com>
            : Added support for warnings, reminders and
            : checks for duplicate tasks b4 adding
"""

__version__   = "0.1.1-py"
__revision__  = "$Revision$"
__date__      = "2007/07/17"
__author__    = "Graham Davies (grahamdaviez@gmail.com)"
__copyright__ = "Copyleft 2006, Graham Davies"
__license__   = "GPL"
__history__   = "See http://todo-py.googlecode.com/svn/trunk/CHANGELOG"

import todo, re, sys, os, getopt, time

# Local override - leave blank to use the normal todo.py directory
TODO_DIR = ''

# Verbose - display extra info when running
verbose = False

# quiet - print nothing except errors, useful for cron
quiet = False

# keepREM = True retains the reminder date string when copying into todo.txt
keepREM = False

def help():
    # print __doc__
    text = """
todo_cron.py Cron Helper for todo.py %s %s
Usage: todo_cron.py [options]

Adds tasks from recur.txt that match today's date to todo.txt file
Requires todo.py to be in the PATH or same directory
Should be run once per day to avoid duplicates (*todo)
** Now checks for duplicate tasks before adding: 2007/07/25 <schliden@gmail.com> **
Example crontab entry: 00 05 * * * /home/user/bin/todo_cron.py
Date format based on that used by remind:

{Wed} Take out trash
{Mon Wed Fri} backup filesystem
{29} pay rent check every month on the 29th
{1 15} do on 1st and 15th day of the month
{Nov 29} @email birthday card every year to someone
{Nov 22 2007} Eat turkey
{Nov 27 *5} Keep adding task for 5 days after event
{Dec 01 +3} Add task 5 days before specified date

Options:
 -h, --help     : Display this message
 -V,  --version : Print version number
 -d, --todo-dir : Use specified directory for files
""" % (__version__, __revision__[1:-1])
    print text
    sys.exit()

def setDirs(dir):
    global RECUR_FILE, RECUR_BACKUP

    RECUR_FILE   = dir + os.path.sep + "recur.txt"
    RECUR_BACKUP = dir + os.path.sep + "recur.bak"
    TODO_FILE    = dir + os.path.sep + "todo.txt"
    if verbose: print "Using file ", RECUR_FILE
    return True

def singleDay(rem, today):
    """Single Day - recur every month on this date eg. {22}"""
    if rem.isdigit():
        event = time.strptime(rem, "%d")
        if event.tm_mday == today.tm_mday:
            return True, True
        else:
            return True, False
    else:
        return False, False

def singleDoW(rem, today):
    """ Single DayOfWeek - recur if day matches eg. {Mon}"""
    try:
        event = time.strptime(rem,"%a")
        if event.tm_wday == today.tm_wday:
            return True, True
        else: return True, False
    except (ValueError), why:
        return False, False

def monthDay(rem, today, warn=False, rep=False):
    """Month Day - add on this day every year eg. {Nov 22}"""
    try:
        event = time.strptime(rem,"%b %d")
        # new code to handle warnings 2007/07/22
        if warn:
             for i in range(1, warn):
             	 if event.tm_mon == today.tm_mon and (event.tm_mday - i) == today.tm_mday:
             	     return True, True
        # new code to handle repeats 2007/07/22
        if rep:
             for i in range(1, rep):
             	 if event.tm_mon == today.tm_mon and (event.tm_mday + i) == today.tm_mday:
             	     return True, True
        # end new code
        if event.tm_mon == today.tm_mon and event.tm_mday == today.tm_mday:
            return True, True
        else: return True, False
    except (ValueError), why:
        return False, False

def monthDayYear(rem, today, warn=False, rep=False):
    """ Month Day Year - single event that doesn't recur eg. {Nov 22 2007}"""
    try:
        event = time.strptime(rem,"%b %d %Y")
        if (event.tm_year == today.tm_year and event.tm_mon == today.tm_mon
                and event.tm_mday == today.tm_mday):
            return True, True
        else: return True, False
    except (ValueError), why:
        return False, False

def hasWarning(rem, today):
    """Month Day Warning - add Warning days before the date eg. {Nov 22 +5}"""
    re_rem = re.compile(r" \+(\d+)$")
    match = re.search(re_rem, rem)
    if match:
        rem = re.sub(re_rem, "", rem)
        return match.group(1), rem
    else:
        return False, False

def hasRepeat(rem, today):
    """Month Day Repeat - add for Repeat days after the date eg. {Nov 22 *5}"""
    re_rem = re.compile(r" \*(\d+)$")
    match = re.search(re_rem, rem)
    if match:
        rem = re.sub(re_rem, "", rem)
        return match.group(1), rem
    else:
        return False, False

def multiDoW(rem, today):
    """Multiple DayOfWeek - recur each day that matches
    eg. {Mon Wed} or {Mon Tue Wed} or {Mon Tue Wed Thu Fri}"""
    words = rem.split()
    for day in words:
        type, now = singleDoW(day, today)
        if not type:
            # If one fails - they all fail
            return False, False
        if now:
            return True, True
    return True, False

def multiDay(rem, today):
    """Multiple Days - recur each day that matches eg. {1 14 28}"""
    words = rem.split()
    for day in words:
        type, now = singleDay(day, today)
        if not type:
            # If one fails - they all fail
            return False, False
        if now:
            return True, True
    return True, False

def parseREM(rem):
    """parses REM style date strings - returns True if event is today"""

    today = time.localtime()

    warnDays, newrem = hasWarning(rem, today)
    if warnDays:
        warnDays = int(warnDays)
        rem = newrem

    repeatDays, newrem = hasRepeat(rem, today)
    if repeatDays:
        repeatDays = int(repeatDays)
        rem = newrem

    type, now = singleDay(rem, today)
    if type and now: return True
    if type and not now: return False

    type, now = multiDay(rem, today)
    if type and now: return True
    if type and not now: return False

    type, now = singleDoW(rem, today)
    if type and now: return True
    if type and not now: return False

    type, now = multiDoW(rem, today)
    if type and now: return True
    if type and not now: return False

    type, now = monthDay(rem, today, warn=warnDays, rep=repeatDays)
    if type and now: return True
    if type and not now: return False

    type, now = monthDayYear(rem, today, warn=warnDays, rep=repeatDays)
    if type and now: return True
    if type and not now: return False

    # 1st DayOfWeek after date
    # {Mon 15}

    # xth DayOfWeek after date
    # {Mon 15}

    # OMIT

    #### Sub day --- no support planned
    # Times -- AT 5:00PM
    # {AT 5:00PM}

def addTodayTasks(file):
    """Add tasks occuring today from a file to the todo list"""
    rem = todo.getDict(file)
    for k,v in rem.iteritems():
        if verbose: print "%3d: %s" % (k, v)
        re_date = re.compile(r"{([^}]+)} ")
        date = re.search(re_date, v)
        if date:
            isToday = parseREM(date.group(1)) # date.group(1) = date in Remind format: Wed, 18 +3, Jan 26 +4
            if isToday:
                task = re.sub(re_date, "", v)
                if taskExists(task):
                    if verbose: print "Exists: " + task
                    continue
                todo.add(task)
        else:
            if verbose: print "No date found for ", v

# new code to handle dupes 2007/07/25
def taskExists(rem):
    """Check for existing tasks in the TODO file"""
    tasks = todo.getTaskDict()
    theSet = set(tasks.values())
    if rem in theSet:
        return True
    else:
        return False

if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hVvqd:',\
            ['help', 'version','todo-dir='])
    except (getopt.GetoptError), why:
        print "Sorry - option not recognized.  Try -h for help"
        sys.exit()


    for o, a in opts:
        if o in ["-h"]:
            help()
        if o in ["-V", "--version"]:
            print __version__, __revision__[1:-1]
            sys.exit()
        if o in ['-v']:
            """Specify verbose from command line"""
            todo.verbose = True
            verbose = True
        if o in ['-q']:
            """Specify quiet from command line"""
            todo.quiet = True
            quiet = True
        if o in ['-d', '--todo-dir']:
            """Specify TODO_DIR from command line"""
            TODO_DIR = a

    # Options processed - ready to go
    todo.setDirs(TODO_DIR)
    setDirs(todo.TODO_DIR)

    # TODO Add checks to see that we are only run once per day
    if (len(args) < 1):
        """ Default action - should probably be help """
        addTodayTasks(RECUR_FILE)
