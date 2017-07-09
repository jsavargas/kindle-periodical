kindle-periodical (beta)
=================
This is a fork from [vncprado/kindle-periodical](https://github.com/vncprado/kindle-periodical) for Python 2.

kindle-periodical is a util in Python 3 for generating kindle .mobi files in periodical style.
The script require KindleGen software in 'kindle/bin' folder. KindleGen is a software develop by Amazon. For download, go to [KindleGen page](https://www.amazon.com/gp/feature.html?docId=1000765211).

**You can run a simple test with just:**
    
    from kindle import Periodical
    
    metadata = {
        "title": "Periodical Title",
        "creator": "Creator Name",
        "publisher": "Publisher Name",
        "subject": "Periodical",
        "description": "Set of news articles in one .mobi file",
        # after make .mobi periodical, the filename will be: Periodical_yyyy-mm-dd
        "filename": "Periodical"
    }
    
    content = [
        {
            "title": "Subscription title 1",
            "items": [
                {
                    # optional
                    "author": "Author Name",
                    # timestamp
                    "published": 1425314310227,
                    # for HTML, use json.dumps() encoding
                    "content": "<b>Insert HTML here.</b>",
                    "title": "Content Title 1"
                },
                {
                    "author": "Author Name",
                    "published": 1425314310227,
                    "content": "<b>Insert HTML here.</b>",
                    "title": "Content Title 2"
                },
                {
                    "author": "Author Name",
                    "published": 1425314310227,
                    "content": "<b>Insert HTML here.</b>",
                    "title": "Content Title 3"
                }
            ]
        },
        {
    
            "title": "Another subscription title 1",
            "items": [
                {
                    "author": "Author Name",
                    "published": 1425340100784,
                    "content": "<b>Insert HTML here.</b>",
                    "title": "Another content title 1"
                },
                {
                    "author": "Author Name",
                    "published": 1425340100784,
                    "content": "<b>Insert HTML here.</b>",
                    "title": "Another content title 2"
                },
                {
                    "author": "Author Name",
                    "published": 1425340100784,
                    "content": "<b>Insert HTML here.</b>",
                    "title": "Another content title 3"
                }
            ]
        }
    ]
    
    per = Periodical()
    
    # optional, default use cover.jpg in kindle-periodiacal/kindle/images folder
    per.IMAGE_COVER = 'FULLPATH/filename.jpg'
    # optional, default use masthead.jpg in kindle-periodiacal/kindle/images folder
    per.IMAGE_MASTHEAD = 'FULLPATH/filename.jpg'
    # optional, default kindle-periodiacal/temp folder
    per.BOOK_DIR_TEMP = 'FULLPATH'
    
    per.set_metadata(metadata)
    per.set_content(sites_content)
    
    # make .mobi periodical and return the full path file
    print(per.make_periodical())

---

**Note:**
For better results, use the old KindleGen 1.1 (search on internet): 


![Alt text](http://i.imgur.com/d9c2S2f.png "Periodical generated with KindleGen 1.1") 

This is a periodical generated with the current (2017-07-01) KindleGen 2.9: 


![Alt text](http://i.imgur.com/4taStRP.png "Periodical generated with KindleGen 2.9")

**TODO**
- Testing for Windows and GNU-Linux machines.
