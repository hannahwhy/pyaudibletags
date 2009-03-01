# $Id: organizaa.py 734 2009-03-01 11:18:23Z  $
# Program to go through a subtree of audiobooks in Audible .aa format, and reorganize the subtree
# with one folder per author and one subfolder per title (which will contain only one .aa file if
# the audiobook comes in a single part.


import sys
import os
import os.path
from pyaudibletags import aafile
import re

try:
    root = sys.argv[1] # This is the subtree to be reorganized
except IndexError:
    raw_input('You must specify a folder to process, for example\n\torganizaa "C:\My Audiobooks"\nPress Enter to continue...')
    sys.exit(1)

unabridged = re.compile(ur" *(\( *)?Unabridged( *\))?",re.I)
selections = re.compile(ur" *(\( *)?Selections( *\))?",re.I)
notallowed = re.compile(ur'[\/:*?"<>|]')

if sys.platform == "win32":
    fndelim=" "
else:
    fndelim="_"
    
counter = 0
errors  = 0

def good_filename(name):
    name = unabridged.sub("",name)
    name = selections.sub("",name)
    name = name.split(":")[0].strip()   # Treat everything after the colon as a subtitle
    name = notallowed.sub("",name)
    name = name.rstrip(".")             # In FAT-32 if you do "md mydir..." it actually creates mydir which means that the name we asked for isn't there when we need it
    
    name = fndelim.join(name.split())
    return name.encode("latin-1")

for dirpath, dirs, files in os.walk(root):
    for name in files:
        if not name.endswith(".aa"):
            continue
        oldname = os.path.join(dirpath,name)
        try:
            aa = aafile(oldname)
        except IOError, details:
            print "Skipping %s. Could not process tags in the header because the file appears to be corrupt:\n%s" % (oldname, details)
            errors += 1
            continue
        author = good_filename(aa.author[0])
        title  = good_filename(aa.parent_title)
        newname = os.path.join(root,author,title,name)
        if os.path.normpath(os.path.normcase(oldname)) == os.path.normpath(os.path.normcase(newname)):
            continue
        try:
            os.renames(oldname, newname)
        except OSError, details:
            print "Skipping %s. Could not rename to %s because the operating system reported the following problem:\n%s" % (oldname, newname, details)
            errors += 1
            continue
        counter += 1
        
print "%d files moved, %d errors" % (counter, errors)

