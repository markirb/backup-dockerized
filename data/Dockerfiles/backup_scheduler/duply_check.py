#!/usr/bin/env python

# By Arne Schwabe <arne-nagios@rfc2549.org>
# LICENSE: BSD

from subprocess import Popen,PIPE
import sys
import time
import os
import argparse
import re

def main():
    parser = argparse.ArgumentParser(description='Duplicity parser')

    parser.add_argument("-w", dest="warninc", default="28h", type=str, 
                        help="Number of seconds allowed for incremential backup warning level")
    parser.add_argument("-W", dest="warnfull", default="32D", type=str, 
                        help="Number of seconds allowed for full backup critical level")
    parser.add_argument("-c", dest="critinc", default="48h", type=str, 
                        help="Number of seconds allowed for incremental backup warning level")
    parser.add_argument("-C", dest="critfull", default="64D", type=str, 
                        help="Number of seconds allowed for full backup critical level")

    args = parser.parse_args()
    
    okay = 0

    args.warninc  = intstringtoseconds(args.warninc)
    args.warnfull = intstringtoseconds(args.warnfull)
    args.critinc  = intstringtoseconds(args.critinc)
    args.critfull = intstringtoseconds(args.critfull)

    output = sys.stdin.read()

    lastfull, lastinc = findlastdates(output)

    sincelastfull = time.time() - lastfull 
    sincelastinc  =  time.time() - lastinc 
    msg = "OK: "
    
    if sincelastfull > args.warnfull or sincelastinc > args.warninc:
        okay = 1
        msg = "WARNING: "
    
    if sincelastfull > args.critfull or sincelastinc > args.critinc:
        okay = 2
        msg = "CRITICAL: "

    if not checkoutput(output):
        okay = 3
        msg = "UNKNOWN: duply output: %s " % repr(output)


    print msg, "last full backup was %s ago, last incremental backup %s ago" % ( formattime(sincelastfull), formattime(sincelastinc) )
    sys.exit(okay)

def checkoutput(output):
    if output.find("No orphaned or incomplete backup sets found.")==-1:
        return False

    return True

def formattime(seconds):
    days = seconds / (3600 * 24)
    hours = seconds / 3600 % 24

    if days:
        if days > 200:
            return "NEVER"
        else:
            return "%d days %d hours" % (days,hours)
    else:
        return "%d hours" % hours


def findlastdates(output):
    lastfull = 0
    lastinc = 0

    for line in output.split("\n"):
        parts = line.split()

        # ['Incremental', 'Sun', 'Oct', '31', '03:00:04', '2010', '1']
        if len (parts) == 7 and parts[0] in ["Full","Incremental"]:
            foo = time.strptime(" ".join(parts[1:6]),"%a %b %d %H:%M:%S %Y")

    
            backuptime =  time.mktime(foo)
    
            if parts[0] == "Incremental" and lastinc < backuptime:
                lastinc = backuptime
            elif parts[0] == "Full" and lastfull < backuptime:
                lastfull = backuptime
        

    # Count a full backup as incremental backup
    lastinc = max(lastfull,lastinc)
    return (lastfull, lastinc)
            
# intstringtoseconds picked up from Duplicity code
bad_interval_string = """Bad interval string "%s"

Intervals are specified like 2Y (2 years) or 2h30m (2.5 hours).  The
allowed special characters are s, m, h, D, W, M, and Y.  See the man
page for more information."""

_interval_conv_dict = {"s": 1, "m": 60, "h": 3600, "D": 86400,
                       "W": 7 * 86400, "M": 30 * 86400, "Y": 365 * 86400}

_interval_regexp = re.compile("^([0-9]+)([smhDWMY])")

class TimeException(Exception):
    pass

def intstringtoseconds(interval_string):
    def error():
        print (bad_interval_string % interval_string)
        sys.exit(2)

    if interval_string.isdigit():
      interval_string = interval_string + 's'

    if len(interval_string) < 2:
        error()

    total = 0
    while interval_string:
        match = _interval_regexp.match(interval_string)
        if not match:
            error()
        num, ext = int(match.group(1)), match.group(2)
        if ext not in _interval_conv_dict or num < 0:
            error()
        total += num * _interval_conv_dict[ext]
        interval_string = interval_string[match.end(0):]
    return total

if __name__=='__main__':
   main()
