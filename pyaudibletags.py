# $Id$

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
import datetime
import time
import re

# The table of contents describes the layout of the file as triples of integers (<section>, <offset>, <length>).
# The method toc() returns the following string translations of <section> where these are known.
# Unknown ones are returned as "Offset <section>".
locations =      {0: "Whole file",
                  1: "Header terminator",
                  2: "Content tags",
                  10:"Audio",
                  11:"Cover art"}

partindication = re.compile(",? *Part *\d+ *$", re.IGNORECASE) 
copyright = re.compile("&#169; *|\(C\);? *")              # Unicode 00A9
mechanical_copyright = re.compile("&#169; *|\(P\);? *")   # Unicode 2117
etal = re.compile(',? *(and|with) more *$')
AandB = re.compile(r'\band\b')

class aafile():
    
    __slots__ = ['short_title','user_alias','category_subcategory_search','pubdate','narrator',
                 'parent_title', 'keywords', 'long_description', 'copyright', 'title', 'is_aggregation',
                 'parent_id', 'codec', 'provider', 'short_description', 'aggregation_id', 'description',
                 'price', 'product_id', 'pub_date_start', 'country', 'title_id', 'author', 
                 'category_search', 'part_number' ]

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
            raise IOError, 'Expecting %d tags from header, got %d' % (expected_tags, len(tags))
        return tags
    
    def __nullcheck(self, key, default=None):
	try:
	    tag = self.__tags[key]
	    if not tag:
		return default
	    return unicode(tag, 'latin-1', 'replace')
	except KeyError:
	    return default

    def get_short_title(self):
	try:
	    return unicode(self.__tags['Content:short_title'].strip(),'latin-1','replace')
	except IndexError:
	    return self.title
	
    def get_user_alias(self):
	return self.__nullcheck('Content:user_alias')

    def get_category_subcategory_search(self):
        cats = tuple([element.strip() for element in self.__nullcheck('Content:category_subcategory_search', '').split(',')])
	if cats == ('',):
	    return self.category_search

    def get_pubdate(self):
	try:
	    return datetime.date(*(time.strptime(self.__tags['Content:pubdate'], '%d-%b-%Y')[0:3]))
	except ValueError:
	    return datetime.date(*(time.strptime(self.__tags['Content:pubdate'], '%d-%b-%y')[0:3]))
	except IndexError:
	    return None

    def get_narrator(self):
	narrator = etal.sub("...",self.__tags['Content:narrator'])
	narrator = AandB.sub(",",narrator)
	return tuple([unicode(element.strip(), 'latin-1', 'replace') for element in narrator.split(',')])

    def get_parent_title(self):
	try:
	    ptitle = unicode(self.__tags['Content:parent_title'].strip(), 'latin-1', 'replace')
	except KeyError:
	    ptitle = None
	if ptitle:
	    return ptitle
	else:
	    return partindication.sub("", self.short_title, 1)
	    
    def get_keywords(self):
	try:
	    return tuple([unicode(element.strip(),'latin-1','replace') for element in self.__tags['Content:keywords'].split(',')])
	except IndexError:
	    return ()

    def get_long_description(self):
	try:
	    return unicode(self.__tags['Content:long_description'].strip(),'latin-1', 'replace')
	except IndexError:
	    return self.description

    def get_copyright(self):
	try:
	    c = unicode(self.__tags['Content:copyright'].strip(), 'latin-1', 'replace')
	    c = copyright.sub("\U00A9", c)
	    c = mechanical_copyright.sub("\U00A9", c)
	    return c
	except IndexError:
	    return ""

    def get_title(self):
	return self.__nullcheck('Content:title')

    def get_is_aggregation(self):
	return self.__nullcheck('Content:is_aggregation', u'no')

    def get_parent_id(self):
	try:
	    return  tuple([unicode(element,'latin-1','replace') for element in self.__tags['Content:product_id'].split('_')])
	except IndexError:
	    prodid = self.product_id
	    if self.is_aggregation == u'no':
		return prodid[:3]
	    else:
		return (prodid[0], prodid[1], prodid[2][:-1])

	return self.__nullcheck('Content:parent_id')

    def get_codec(self):
	return self.__nullcheck('Content:codec')

    def get_provider(self):
	return self.__nullcheck('Content:provider')

    def get_short_description(self):
	try:
	    return unicode(self.__tags['Content:short_description'].strip(),'latin-1', 'replace')
	except IndexError:
	    return self.description

    def get_aggregation_id(self):
	try:
	    return tuple([unicode(element,'latin-1','replace') for element in self.__tags['Content:aggregation_id'].split('_')])
	except IndexError:
	    return self.parent_id

    def get_description(self):
	try:
	    desc = self.__tags['Content:short_description'].strip()
	    if not desc:
		return self.title
	    return unicode(desc,'latin-1', 'replace')
	except IndexError:
	    return self.title

    def get_price(self):
	try:
	    return float(self.__tags['Content:price'])
	except ValueError:
	    return 0.00

    def get_product_id(self):
	try:
	    return  tuple([unicode(element,'latin-1','replace') for element in self.__tags['Content:product_id'].split('_')])
	except IndexError:
	    return ()

    def get_pub_date_start(self):
	try:
	    try:
		return datetime.date(*(time.strptime(self.__tags['Content:pub_date_start'], '%d-%b-%Y')[0:3]))
	    except ValueError:
		return datetime.date(*(time.strptime(self.__tags['Content:pub_date_start'], '%d-%b-%y')[0:3]))
	except IndexError:
	    return self.pubdate

    def get_country(self):
	try:
	    return int(self.__tags['Content:country'])
	except ValueError, IndexError:
	    return 0

    def get_title_id(self):
	try:
	    return  tuple([unicode(element,'latin-1','replace') for element in self.__tags['Content:title_id'].split('_')])
	except IndexError:
	    return ()

    def get_author(self):
	author = etal.sub("...",self.__tags['Content:author'])
	author = AandB.sub(",",author)
	return tuple([unicode(element.strip(), 'latin-1', 'replace') for element in author.split(',')])

    def get_category_search(self):
        cats = tuple([element.strip() for element in self.__nullcheck('Content:category_search', '').split(',')])
	if cats == ('',):
	    return ()
	else:
	    return cats

    def get_part_number(self):
	if self.is_aggregation == u'no':
	    return 0
	else:
	    return int(self.title_id[2][-1],36) - 9
	
    def get_unabridged(self):
	return  u"Unabridged" in self.title

    def get_selections(self):
	return  u"Selections" in self.title

    short_title = property(get_short_title, doc="Docstring for attribute short_title")

    user_alias = property(get_user_alias, doc="Docstring for attribute user_alias")

    category_subcategory_search = property(get_category_subcategory_search, doc="Docstring for attribute category_subcategory_search")

    pubdate = property(get_pubdate, doc="Docstring for attribute pubdate")

    narrator = property(get_narrator, doc="Docstring for attribute narrator")

    parent_title = property(get_parent_title, doc="Docstring for attribute parent_title")

    keywords = property(get_keywords, doc="Docstring for attribute keywords")

    long_description = property(get_long_description, doc="Docstring for attribute long_description")

    copyright = property(get_copyright, doc="Docstring for attribute copyright")

    title = property(get_title, doc="Docstring for attribute title")

    is_aggregation = property(get_is_aggregation, doc="Docstring for attribute is_aggregation")

    parent_id = property(get_parent_id, doc="Docstring for attribute parent_id")

    codec = property(get_codec, doc="Docstring for attribute codec")

    provider = property(get_provider, doc="Docstring for attribute provider")

    short_description = property(get_short_description, doc="Docstring for attribute short_description")

    aggregation_id = property(get_aggregation_id, doc="Docstring for attribute aggregation_id")

    description = property(get_description, doc="Docstring for attribute description")

    price = property(get_price, doc="Docstring for attribute price")

    product_id = property(get_product_id, doc="Docstring for attribute product_id")

    pub_date_start = property(get_pub_date_start, doc="Docstring for attribute pub_date_start")

    country = property(get_country, doc="Docstring for attribute country")

    title_id = property(get_title_id, doc="Docstring for attribute title_id")

    author = property(get_author, doc="Docstring for attribute author")

    category_search = property(get_category_search, doc="Docstring for attribute category_search")
    
    part_number = property(get_part_number, doc="Return an integer in the range 1-27 indicating the part number of a multipart audiobook; zero if there is only one part")
    
    unabridged = property(get_unabridged, doc="Return True if the title is an unabridged performance of the original (as specified in the title) or False otherwise")
    
    selections = property(get_selections, doc="Return True if the title contains selections from the original work (as specified in the title) or False otherwise")

if __name__ == "__main__":
    aa = aafile(r"F:\Documents\Audio Books\Bernard Cornwell and Susannah Kells\Unknown Album\A Crowning Mercy (Unabridged), Part 1.aa")
    for att in aa.__slots__:
	print "%s=%r" % (att, getattr(aa,att))
    


