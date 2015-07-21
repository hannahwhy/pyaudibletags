Audiobook files in `.aa` format from [Audible Inc](http://www.audible.com) contain content tags for such things as author, title, narrator; information that is otherwise grandly called _metadata_.

Audible does not publish a specification for the file format, which means that you can only access these tags from software or devices that are capable of playing the audiobooks. Windows File Manager will also display the data in a tooltip over the file if you have that switched on.

But programmatic access to these tags is necessary for organizing your audiobook library.

Apple's iTunes will do the organization if you ask, but not very well: it will create separate folders for authors but lumps all books by that author into a single subfolder called "Unknown Album".

Audible's own Audible Manager program actually expects you to keep your audiobooks in a single huge directory, or else create and maintain author and book folders _manually_.

This is a small Python module that will return the content tags, and other information, that is to be found in the `.aa` file header. I wrote this module because I needed it and a diligent internet search failed to turn up anything that someone else had already written.

You can use this information in a Python program to move files around into a folder structure of your own choosing, or produce reports or catalogues, or build a search tool. If you don't think your Python is up to writing such a program, the project includes a sample that accomplishes the first task.

Since there isn't a published specification, the information returned is based on guesswork, and some of it is only of use to the codec. Nearly all of it can be picked out by eye by reading the first 4k of the .aa file into a hex editor. You won't find anything in this module that will help you to decompress or decrypt the file.

You can't use this module to modify the tags and write them back to the `.aa` file, for the simple reason that Audible's download process creates a fresh file for you with your user name and account number in the header, which is then checksummed. Rewriting the header with different tags would break the checksum and corrupt the file.

This only works with `.aa` files. Audible's newer "enhanced audio" files with the extension `.aax` have a completely different layout that this module does not understand. If you try to read an `.aax` file with this module, you will get the IOError _filename_ is _n_ bytes but its header thinks it contains 36 bytes.

To extract metadata from `.aax` files, use [Mutagen](https://bitbucket.org/lazka/mutagen): tell it that the `.aax` is an `.m4a` file and it will retrieve metadata for you.