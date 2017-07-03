kindle-periodical (experimental)
=================
This is a fork from [vncprado/kindle-periodical](https://github.com/vncprado/kindle-periodical) for Python 2.

kindle-periodical is a util in Python 3 for generating kindle .mobi files in periodical style.
The script require KindleGen software in 'kindle/bin' folder. KindleGen is a software develop by Amazon. For download, go to [KindleGen page](https://www.amazon.com/gp/feature.html?docId=1000765211).

The folder 'kindle/templates' have a set of templates to generated .opf, .ncx, articles and content.html files, necesary for KindleGen software. You can modify them as you like.

The folder 'kindle/data-templates' contains the two JSON data files of the texts and metadata that make up the .mobi periodical. For production environments these files must go in the 'kindle/temp/data' folder.


You can run a simple test with just:
    
    $ python kindle/periodical.py

####To-Do
- Add cover image for .mobi periodical.
- Add images for articles.
- Testing for Windows and GNU-Linux machines.
