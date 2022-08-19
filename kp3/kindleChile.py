# For HTML content use json.dumps() method.
import re
import json
import feedparser

from kp3 import Periodical
from subscription.chile.elmostrador import ElMostrador



Mostrador = ElMostrador()

items = Mostrador.get_content()

print( 'Number of RSS posts :', len(items))


content = []
content.append({'title': 'El Mostrador', "items": items })

metadata = {
    "title": "KindlePeriodical El Mostrador",
    "creator": "Creator Name",
    "publisher": "El Mostrador",
    "subject": "KindlePeriodical",
    "description": "Set of news articles in one .mobi file",
    # after make .mobi periodical, the filename will be: Periodical_yyyy-mm-dd
    "filename": "KindlePeriodicalChile"
}


print("*"*40)


per = Periodical()

# Optional, default use cover.jpg in kindle-periodiacal/kindle/images folder
per.IMAGE_COVER = 'FULLPATH/filename.jpg'

# Optional, default use masthead.jpg in kindle-periodiacal/kindle/images folder
per.IMAGE_MASTHEAD = 'FULLPATH/filename.jpg'

# Optional, default ~/temp folder
per.BOOK_DIR_TEMP = '/output'

# Example: /bin
per.KINDLEGEN_PATH = 'FULLPATH'

per.set_metadata(metadata)
per.set_content(content)

# make .mobi periodical and return the full path file
print(per.make_periodical())
