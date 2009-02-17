# $Id:$

# Audiobook files in .aa format from Audible Inc contain content tags for such things as author, title, narrator;
# information that is otherwise grandly called metadata.
#
# Audible does not publish a specification for the file format, which means that you can only access these tags
# from software or devices that are capable of playing the audiobooks.
#
# But programmatic access to these tags is necessary for organizing your audiobook library.
#
# Apple's iTunes will do the organization if you ask, but not very well: it will create separate folders for
# authors but lumps all books by that author into a single subfolder called "Unknown Album".
#
# Audible's own Audible Manager program actually expects you to keep your audiobooks in a single huge directory,
# or else create and maintain author and book folders manually.
#
# This is a small Python module that will return the content tags, and other information, that is to be found in
# the .aa file header. You can use this information in a Python program to move files around into a folder structure
# of your own choosing, or produce reports or catalogues, or build a search tool.
#
# Since there isn't a published specification, the information returned is based on guesswork, and some of it is
# only of use to the codec. Nearly all of it can be picked out by eye by reading the first 4k of the .aa file into
# a hex editor. You won't find anything in this module that will help you to decompress or decrypt the file.

import os
import struct

# The table of contents describes the layout of the file as triples of integers (<section>, <offset>, <length>).
# The method toc() returns the following string translations of <section> where these are known.
# Unknown ones are returned as "Offset <section>".
locations =      {0: "Whole file",
                  1: "Header terminator",
                  2: "Content tags",
                  10:"Audio",
                  11:"Cover art"}

class aafile():

    def __init__(self, afile):
        self.__toc = ()
        if type(afile) is str:
            self.filename = afile
            self.ossize = os.stat(self.filename).st_size
            self.f = file(self.filename,'rb')
            try:
              self.__tags = self.__get_headers(self.f)
            finally:
              self.f.close()
        elif type(afile) is file:
            if afile.closed:
                raise IOError, "Cannot analyze a closed file" 
            self.f = afile
            self.filename = self.f.name
            self.ossize = os.stat(self.filename)
            self.__tags = self.__get_headers(self.f)

    def headers(self):
        """Returns a dictionary of 5 data items from the very beginning of the file:
           Filesize: The size the file believes itself to be, in bytes, to detect truncated copies.
           Magic: The constant 1469084982 which identifies the file as being an Audible file.
           TOC size: Number of entries in the table of contents, as returned by toc().
           Number of content tags: Number of entries in the tag table, as returned by tags().
           Magic2: Magic repeated at the end of the table of contents.
        """
        return dict([(k[7:],v) for (k,v) in self.__tags.items() if k.startswith('Leader')])

    def toc(self):
        """Returns a dictionary of (usually) 12 data items giving the location of various
           sections of the file as (offset, length). All are returned but the functions of
           only some are known: these are listed in the dictionary locations.
        """
        return dict([(k[4:],v) for (k,v) in self.__tags.items() if k.startswith('TOC')])

    def rawtoc(self,formatted=0):
        """Returns the same data as headers() + toc() but untranslated as (usually) 48 integers
           and laid out exactly as they appear in the first (usually) 192 bytes of the file.
        """
        if formatted:
          return ("%13d%13d%13d%13d\n"  + "%13d%13d%13d\n"*self.__toc[2] + "%13d%13d%13d%13d\n" * 2) % self.__toc
        else:
          return self.__toc[:]

    def tags(self):    
        """Returns a dictionary of around 30 tags describing the audio content of the file
           (as opposed to file layout). The exact repertoire of tags varies and is richer
           with more recently published titles. This means that you cannot rely on a particular
           tag being present. The markup of text fields is not always the same.
           * The tags author and narrator may return comma-separated lists of names.
           * The description tags have single quotes that are sometimes \'escaped\', C-style,
             and sometimes not.
           * The description tags may contain html markup such as <I>...</I>
           * The copyright tag may contain html entities such as &#169;
           Books that come in multiple parts have Part 1, Part 2 etc in the individual titles;
           they may also have a parent title tag that gives the book title alone, but this is
           not always present. Such books have the tag is_aggregation=collection and will
           have a parent_id tag in addition to the title_id tag.
           The tags HeaderSeed, HeaderKey, EncryptedBlocks and 68ec733412b9 are always present
           and do not really fit the description of describing the audio content, since they
           appear to support the checksumming of the header and the encryption of the content,
           but they exist in the tag table along with and (to a program) indistinguishable
           from the others.
        """
        return dict([(k[8:],v) for (k,v) in self.__tags.items() if k.startswith('Content')])

    def metadata(self):
        return self.__tags.copy()
                  
    def __get_headers(self, f):
        tags = {}
        header1=f.read(12)
        self.__toc = struct.unpack('!3i',header1)
        if self.__toc[0] != self.ossize:
            raise IOError, "%s is %d bytes but its header thinks it contains %d bytes"  % (self.filename,self.ossize,self.__toc[0])
        if self.__toc[1] != 1469084982:
            raise IOError, "%s does not appear to be an .aa file" % (self.filename,)
        tablesize = self.__toc[2] * 3
        f.seek(0)
        expanded_size = tablesize*4 + 48
        header1=f.read(expanded_size)
        self.__toc = struct.unpack('!%di' % (expanded_size//4), header1)
        tags["Leader:Filesize"  ] = self.__toc[0]
        tags["Leader:Magic"     ] = self.__toc[1]
        tags["Leader:TOC size"  ] = self.__toc[2]
        for c in range(self.__toc[2]):
            index = 4 + c * 3
            offsetname = locations.get(self.__toc[index],"Offset %d" % self.__toc[index])
            tags["TOC:"+offsetname] = self.__toc[index+1:index+3]
        tags["Leader:Magic2"       ] = self.__toc[tablesize + 5]
        tags["Leader:#Content tags"] = self.__toc[tablesize + 10]

        expected_tags = self.__toc[46]+len(tags)
        f.seek(tags["TOC:Content tags"][0])
        header2 = f.read(tags["TOC:Content tags"][1]+1)
        p = 5
        
        while len(tags) < expected_tags:
            lengths = struct.unpack('!ii',header2[p:p+8])
            fmt=("!%ds%dsc" % lengths)
            p += 8
            q = sum(lengths)+1
            tagpair = struct.unpack(fmt,header2[p:p+q])
            tags["Content:"+tagpair[0]]=tagpair[1]
            p += q

        if len(tags) != expected_tags:
            raise RuntimeError, 'Expecting %d tags from header, got %d' % (expected_tags, len(tags))
        return tags
