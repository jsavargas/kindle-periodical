import re
import json
import feedparser




class ElMostrador:

    RSS = 'https://www.elmostrador.cl/destacado/feed/'


    def get_entries(self):
        NewsFeed = feedparser.parse(self.RSS)
        entry = NewsFeed.entries[1]

        return NewsFeed.entries


    def get_content(self):

        entries = self.get_entries()
        
        items = []

        for entrie in entries:
            econtent = entrie.content
            txt = (econtent[0].value) #.replace("<strong>También te puede interesar:</strong>","")
            txt = txt.replace("<strong>También te puede interesar:</strong>","")
            txt = txt.replace("<strong>Te puede interesar también:</strong>","")

            pattern = re.compile(r"<li>.*</li>")
            txt = pattern.sub("", txt)
            pattern = re.compile(r"<ul>")
            txt = pattern.sub("", txt)
            pattern = re.compile(r"</ul>")
            txt = pattern.sub("", txt)

            items.append({"author": "El Mostrador", "published": 1507343103, "content": f'<div align="justify">{txt}</div>', "title": entrie['title']})


        return items