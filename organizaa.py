# $Id$
# Program to go through a subtree of audiobooks in Audible .aa format, and reorganize the subtree
# with one folder per author and one subfolder per title (which will contain only one .aa file if
# the audiobook comes in a single part.


import sys
import os
import os.path
from pyaudibletags import aafile
import re

root = sys.argv[1] # This is the subtree to be reorganized
unabridged = re.compile(ur" *(\( *)?Unabridged( *\))?",re.I)
selections = re.compile(ur" *(\( *)?Selections( *\))?",re.I)
notallowed = re.compile(ur'[\/:*?"<>|]')

if sys.platform == "win32":
    fndelim=" "
else:
    fndelim="_"
    
counter = 0

def good_filename(name):
    name = unabridged.sub("",name)
    name = selections.sub("",name)
    name = name.split(":")[0].strip()   # Treat everything after the colon as a subtitle
    name = notallowed.sub("",name)
    
    name = fndelim.join(name.split())
    return name.encode("latin-1")

for dirpath, dirs, files in os.walk(root):
    for name in files:
        if not name.endswith(".aa"):
            continue
        oldname = os.path.join(dirpath,name)
        aa = aafile(oldname)
        author = good_filename(aa.author[0])
        title  = good_filename(aa.parent_title)
        newname = os.path.join(root,author,title,name)
        if os.path.normpath(os.path.normcase(oldname)) == os.path.normpath(os.path.normcase(newname)):
            continue
        os.renames(oldname, newname)
        counter += 1
        
print "%d files moved" % counter

