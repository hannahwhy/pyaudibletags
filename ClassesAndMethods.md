# Class `aafile` #

## Constructor ##

`class aafile(filename)`

_filename_ is either a string containing a fully-qualified filename including extension or an open file object

The `aafile` class offers two interfaces: a high-level interface with predictable attributes, and a low-level interface that returns dictionaries presenting what happens to be present in the file. The exact repertoire of physically-present tags varies and is richer with more recently published titles. This means that you cannot rely on a particular tag being present in the file.

The attribute interface hides this messy reality from you and returns predictable data, even if this has to be synthesized from other information in the file. For example, many audiobooks come in multiple parts. Some of them have a `parent_title` tag, which is what one would like to use to make a folder name. But some don't. If you ask for the attribute `parent_title`, but the corresponding tag isn't physically present in the file, the attribute interface will construct a parent title from the title of the part, by removing (say) "Part 1" from the end of the part title.

You could of course do this yourself, and if you want to, the low-level interface is available. But the high-level interface allows you to concentrate on what you are doing with the information in the file, without having to write tedious traps for when the expected data isn't there.

## Instance Attributes ##

All string-valued attributes are returned as Unicode.

### Title and Description ###

  * `title`: Title of the file; for multipart books, will contain a part number.

  * `short_title`: Abbreviated title.

  * `parent_title`: For multipart books, the umbrella title covering all of the parts; for books that come in a single file, the same as `title`.

  * `description`: Publisher's blurb; may stop in mid-sentence.

  * `short_description`: Shorter version of `description`; may be identical to it.

  * `long_description`: Long version of publisher's blurb; may stop in mid-sentence; may be identical to `description`.

  * `part_number`: an integer in the range 1-27 indicating the part number of a multipart audiobook; zero if there is only one part.

### Author and Narrator ###

Books such as compilations may have more than one author. Many recordings have multiple narrators; and where the author provides an introduction or an afterword the author is also listed as a narrator. For this reason these attributes are always tuples.

  * `author`: a tuple of Unicode strings; if there are more than 3 authors the final element of the tuple may be `...` (representing _and more_ or _with more_ in the physical tag).

  * `narrator`: a tuple of Unicode strings; if there are more than 3 narrators the final element of the tuple may be `...`  (representing _and more_ or _with more_ in the physical tag).

### Provenance and Copyright ###

  * `copyright`: copyright notice as it appears in the file, but with copyright symbols translated where required into the appropriate Unicode codepoints.

  * `provider`: publisher of the audiobook.

  * `country`: indication of the territories in which the audiobook may be sold: `0`=worldwide; _other values not known_.

  * `pubdate`: publication date as an object of type `datetime.date`; a suspiciously large number of dates are 1 January: this is may be a conventional indication that only the year is known; 1 January 1970 is a Unix convention that means "date unknown".

  * `pub_date_start`: purpose unknown; mostly absent from the file; in practice, for books, when present in the file, is apparently always equal to `pubdate`; if absent from the file, `pubdate` will be returned.

### Search categories ###

  * `category_search`: a tuple of Audible-defined book categories, for example `('Mystery', 'Detective')` _(not much used; this will mostly return an empty tuple)_.

  * `category_subcategory_search`: a tuple of Audible-defined book categories and subcategories, for example `('Fiction', 'Science Fiction')` _(not much used; this will mostly return an empty tuple)_.

  * `keywords`: a tuple of (one suspects) publisher-defined book categories; domain is highly variable: sometimes indistinguishible from `category` ("Science Fiction"), sometimes lists proper names of characters ("Ender Wiggin", "Amelia Peabody"), sometimes tries to summarize plot ("1700s, passion"); in short of dubious utility.

### Identifiers ###

  * `title_id`: a 3-tuple identifying document type (e.g. `BK` for book), an Audible 4-character code for provider (e.g. `BBCW` for BBC Worldwide); and a catalogue number (with `a`, `b` etc suffixed if the book is in multiple parts).

  * `product_id`: a 4-tuple; first 3 elements as for `title_id`; 4th element same as `codec`.

  * `parent_id`: for an audiobook in multiple parts, an identifier that ties all the parts together; a 3-tuple as for `title_id` but without the `a`, `b` suffix for multiple parts. Not always present in the file; if absent, a value will be synthesized from `product_id`.

  * `aggregation_id`: identical to `parent_id`, except that it is less often physically present in the file; if absent, `parent_id` will be returned.

### Purchase information ###

  * `user_alias`: username at audible.com that paid for the audiobook.

  * `price`: a float representing the price paid for the audiobook; 0.0 if missing.

### Audiobook structure ###

  * `is_aggregation`: indicates whether the file is a part of a multipart audiobook: `no`= not a multipart audiobook; `collection`=is a multipart audiobook; not always present in the file; if absent, `no` will be returned.

  * `codec`: a code corresponding to the Audible compression types: `acelp16`=Audible type 3; `mp332`=Audible type 4.

## Instance Methods ##

Even if you want a low-level interface, the method you probably want is `tags()`. The other methods return data that is primarily of interest in determining where the source data for `tags()` is located.

### `tags()` ###

Returns a dictionary of around 30 tags describing the audio content of the file (as opposed to file layout). The exact repertoire of tags varies and is richer with more recently published titles. This means that you cannot rely on a particular tag being present.

The markup of text fields is not always the same.

  * The tags `author` and `narrator` may return comma-separated lists of names; with compilations the list may be quite long and not really suitable as a folder name
  * The tags `description`, `short_description`, `long_description` have single quotes sometimes \'escaped\', C-style, and sometimes not
  * The `description` tags may contain html markup such as `<I>...</I>`
  * The `copyright` tag may contain html entities such as `&#169;`
  * The `pubdate` and `pub_date_start` fields, when present, may be of the form DD-MMM-YY or DD-MMM-YYYY.

Books that come in multiple parts have Part 1, Part 2 etc in the individual titles; they may also have a `parent_title` tag that gives the book title alone, but this is not always present.

Books that come in multiple parts always have the tag `is_aggregation=collection` and  may have `parent_id` and `aggregation_id` tags in addition to the `title_id` tag.

The tags `HeaderSeed`, `HeaderKey`, `EncryptedBlocks` and `68ec733412b9` are always present and do not really fit the description of describing the audio content, since they appear to support the checksumming of the header and the encryption of the content, but they exist in the tag table along with and (to a program) indistinguishable from the others.

### `headers()` ###

Returns a dictionary of 5 integers from the first (usually) 192 bytes of the file:

  * `Filesize`: The size the file believes itself to be, in bytes; this is presumably used to detect truncated copies.

  * `Magic`: The constant 1469084982 which identifies the file as being an Audible file.

  * `TOC size`: Number of entries in the table of contents, as returned by `toc()`.

  * `Number of content tags`: Number of entries in the tag table, as returned by `tags()`.

  * `Magic2`: Magic repeated at the end of the table of contents.

### `toc()` ###

Returns a dictionary of (usually) 12 integer tuples that make up an offset table giving the location of various sections of the file as (offset, length). All of the tuples in the header are returned but the functions of only some are known: these are:

  * `Whole file`: offset (0) and length of entire file. (Entry 0 in the file.)

  * `Header terminator`: offset and length of the block that terminates the table of contents. (Entry 1 in the file.)

  * `Content tags`: offset and length of the tag table. (Entry 2 in the file.)

  * `Audio`: offset and length of the audio content (not including encryption data and decompression keys). (Entry 10 in the file.)

  * `Cover art`: offset and length of the cover art image data. (Entry 11 in the file.)

Entries in the table whose function is unknown have the key `Offset n` where n is the identifying number (other than 0-2 and 10-11). These numbers do not necessarily appear in the file in ascending order, although entries 0-2 always do. The number of tuples in the offset table is given by `headers()['TOC size']`.

### `rawtoc(formatted=0)` ###

Returns the same data as `headers()` and `toc()` together but untranslated as (usually) 48 integers and laid out exactly as they appear in the first (usually) 192 bytes of the file. If `formatted` is set to 1 then the result is a multi-line string with the numbers laid out with spaces and line breaks to make them easier to understand.

### `metadata` ###

Returns all of the metadata retrieved from the file header in a single dictionary. Dictionary keys have the prefixes `Leader:`, `TOC:` and `Content:`. These prefixes correspond to the methods `headers()`, `toc()` and `tags()` respectively.

# Example: High-level Interface using attributes #

```
import os
import os.path 
from pyaudibletags import aafile 
for root, dirs, files in os.walk(r"F:\My Audiobooks"): 
    for name in files: 
        if not name.endswith(".aa"): 
            continue 
        fullname = os.path.join(root,name) 
        aa = aafile(fullname) 
        print name, aa.author[0], aa.title
```

# Example: Low-level Interface using `tags()` #

```
import os
import os.path 
from pyaudibletags import aafile 
for root, dirs, files in os.walk(r"F:\My Audiobooks"): 
    for name in files: 
        if not name.endswith(".aa"): 
            continue 
        fullname = os.path.join(root,name) 
        aa = aafile(fullname) 
        print name 
        for k,v in aa.tags().items(): 
            print "%-32s%r" % (k, v) 
```