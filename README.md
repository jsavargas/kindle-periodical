kindle-periodical (experimental)
=================
This is a fork from [vncprado/kindle-periodical](https://github.com/vncprado/kindle-periodical) for Python 2.

kindle-periodical is a util in Python 3 for generating kindle .mobi files in periodical style.
The script require KindleGen software in 'kindle/bin' folder. KindleGen is a software develop by Amazon. For download, go to [KindleGen page](https://www.amazon.com/gp/feature.html?docId=1000765211).

The folder 'kindle/templates' have a set of templates to generated .opf, .ncx, necesary for KindleGen software. You can modify them as you like.

The folder 'kindle/data-templates' contains the two JSON data files for the texts and metadata that make up the .mobi periodical. For production environments these files must go in the 'kindle/temp/data' folder.

The folder 'kindle/images' contains two images on .jpg: a cover for kindle periodical and a masthead image (only for KindleGen 1.1).

**You can run a simple test with just:**
    
    $ python kindle/periodical.py

**Note:**
For better results, use the old KindleGen 1.1 (search on internet): 


![Alt text](http://i.imgur.com/d9c2S2f.png "Periodical generated with KindleGen 1.1") 

This is a periodical generated with the current (2017-07-01) KindleGen 2.9: 


![Alt text](http://i.imgur.com/4taStRP.png "Periodical generated with KindleGen 2.9")

**TODO**
- Add images for articles.
- Testing for Windows and GNU-Linux machines.
