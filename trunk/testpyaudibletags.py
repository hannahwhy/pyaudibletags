# $Id$
#Sample usage:
import os.path
from pyaudibletags import aafile
for root, dirs, files in os.walk(r"F:\Documents\Audio Books\Kay Kenyon\The Entire and the Rose"):
    for name in files:
        if not name.endswith(".aa"):
            continue
        fullname = os.path.join(root,name)
        aa = aafile(fullname)
        print name
        for d in (aa.tags(),):
            for k,v in d.items():
                print "%-32s%r" % (k, v)
        

