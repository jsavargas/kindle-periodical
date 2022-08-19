# For HTML content use json.dumps() method.
import re
import json
import feedparser

from kp3 import Periodical

metadata = {
    "title": "KindlePeriodical Title",
    "creator": "Creator Name",
    "publisher": "Publisher Name",
    "subject": "KindlePeriodical",
    "description": "Set of news articles in one .mobi file",
    # after make .mobi periodical, the filename will be: Periodical_yyyy-mm-dd
    "filename": "KindlePeriodicalChile"
}

content = [
    {
        "title": "Subscription title 1",
        "items": [
            {
                # Optional.
                "author": "Author Name",
                # Unix timestamp.
                "published": 1507343103,
                # For HTML, use json.dumps() encoding.
                "content": "<b>Insert HTML here.</b>",
                "title": "Content Title 1"
            },
            {
                "author": "Author Name",
                "published": 1507343103,
                "content": "<b>Insert HTML here.</b>",
                "title": "Content Title 2"
            },
            {
                "author": "Author Name",
                "published": 1507343103,
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
                "published": 1507343103,
                "content": "<b>Insert HTML here.</b>",
                "title": "Another content title 1"
            },
            {
                "author": "Author Name",
                "published": 1507343103,
                "content": "<b>Insert HTML here.</b>",
                "title": "Another content title 2"
            },
            {
                "author": "Author Name",
                "published": 1507343103,
                "content": "<b>Insert HTML here.</b>",
                "title": "Another content title 3"
            }
        ]
    }
]




per = Periodical()

# Optional, default use cover.jpg in kindle-periodiacal/kindle/images folder
per.IMAGE_COVER = 'FULLPATH/filename.jpg'

# Optional, default use masthead.jpg in kindle-periodiacal/kindle/images folder
per.IMAGE_MASTHEAD = 'FULLPATH/filename.jpg'

# Optional, default ~/temp folder
per.BOOK_DIR_TEMP = 'output'

# Example: /bin
per.KINDLEGEN_PATH = 'FULLPATH'

per.set_metadata(metadata)
per.set_content(content)

# make .mobi periodical and return the full path file
print(per.make_periodical())
