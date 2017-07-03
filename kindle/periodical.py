# -*- coding: utf-8 -*-

"""
KINDLE-PERIODICAL for Python 3
This is a fork from vncprado/kindle-periodical for Python 2
https://github.com/vncprado/kindle-periodical
"""

"""
This is the main file that implements kindle periodical generation
All files are generated in temp folder
You need to put a kindlegen binary in bin folder in order to generate .mobi
"""

import os
import sys
import glob
import re
import json
import random
import subprocess
from datetime import datetime
from future.utils import iteritems
from past.builtins import basestring

from templates import *

DEBUG = True
BOOK_DIR_BASE = os.path.abspath(os.path.join(os.path.curdir, os.pardir)) + '/temp/'


class Periodical:
    """
    Class that implements Kindle periodical file generation
    """

    def __init__(self, data, book_directory=BOOK_DIR_BASE,
                 user_id='test_id'):
        self.set_meta(data)
        self.user_id = user_id

        if not os.path.exists(book_directory):
            os.makedirs(book_directory)
        self.book_directory = book_directory

    def set_meta(self, data):
        self.title = data['title']
        self.creator = data['creator']
        self.publisher = data['publisher']
        self.subject = data['subject']
        self.description = data['description']
        self.filename = data['filename'] + '_' + datetime.today().strftime('%Y-%m-%d')

    def fix_encoding(self, input):
        """
        Correcting any wrong encoding
        """

        if isinstance(input, dict):
            return {self.fix_encoding(key):
                    self.fix_encoding(value) for key,
                    value in iteritems(input)}
        elif isinstance(input, list):
            return [self.fix_encoding(element) for element in input]
        if isinstance(input, basestring):
            return input.encode('ascii', 'xmlcharrefreplace').decode('utf-8')
        else:
            return input

    def setup_data(self, data):
        """
        Create/modify description, date, title and content from items
        in subscriptions
        """

        data = self.fix_encoding(data)
        for subscription in data:
            for item in subscription['items']:
                if item['published']:
                    if not 'content' in item.keys():
                        item['content'] = u''
                    else:
                        item['content'] = item['content']
                    item['description'] = self.get_description(item['content'])
                    item['date'] = datetime.fromtimestamp(
                        item['published']/1000).strftime('%d/%m/%Y')

                    if 'title' in item.keys():
                        item['title'] = item['title']
                    else:
                        item['title'] = item['description'][:15]\
                            + ' - ' + item['date']
                    item['id'] = item['id'].replace(':', '-')
                    item['id'] = item['id'].replace('_', '')

        self.data = data

        self.remove_empty_subscriptions()

    def set_content(self, data):
        """
        Main function that creates all necessary files with provided data
        """

        self.setup_data(data)
        if DEBUG:
            print('Setup Data OK')

        self.create_articles()
        if DEBUG:
            print('Articles OK')

        self.create_contents()
        if DEBUG:
            print('Contents OK')

        self.create_opf()
        if DEBUG:
            print('OPF OK')

        self.create_ncx()
        if DEBUG:
            print('NCX OK')

        created_file = self.create_mobi()
        if DEBUG and created_file:
            print('Book', created_file, 'OK!')

        # if DEBUG:
        #     print('Keeping temp files!')
        # else:
        #     deleted = self.delete_temp_files()
        #     if deleted:
        #         print('Temp Files Removed!')

        if self.delete_temp_files():
            print('Temp Files Removed!')

        return created_file

    def create_articles(self):
        """
        Use templates/article.template file to format html article
        creating their files
        """

        for subscription in self.data:
            for item in subscription['items']:
                filename = self.book_directory + item['id'] + '.html'
                if item['published']:
                    description = item['description']
                    date = item['date']
                    title = item['title']
                    content = item['content']
                # {$title} {$creator} {$description} {$title} {$content}
                html_data = ARTICLE_STR.format(title,
                                               subscription['title'],
                                               description,
                                               title,
                                               content,
                                               )

                self.write_file(filename, html_data)

    def create_contents(self):
        """
        Use templates/contents.template file to format content.html file
        """

        filename = self.book_directory + 'contents.html'
        sections = ''
        for subscription in self.data:
            sections = sections + '\t<h4>' + subscription['title'] + '</h4>\n'
            sections = sections + '\t<ul>\n'
            for item in subscription['items']:
                description = item['description']
                date = item['date']
                title = item['title']
                sections = sections \
                           + '\t\t<li><a href="' \
                           + item['id'] \
                           + '.html">' \
                           + title \
                           + '</a></li>\n'
                sections = sections + '\t</ul>\n'

        # {$sections}
        html_data = CONTENTS_STR.format(sections)

        self.write_file(filename, html_data)

    def create_opf(self):
        """
        Use templates/content_opf.template to format content.opf file
        """

        filename = self.book_directory + 'content.opf'

        manifest = ''
        items_ref = ''

        for subscriptions in self.data:
            for item in subscriptions['items']:
                manifest = manifest \
                           + '\t\t<item href="' \
                           + item['id'] \
                           + '.html" media-type="application/xhtml+xml" id="item-' \
                           + item['id'] + '"/>\n'
                items_ref = items_ref \
                            + '\t\t<itemref idref="item-' \
                            + item['id'] \
                            + '"/>\n'

        template_data = {'title': self.title,
                         'creator': self.creator,
                         'publisher': self.publisher,
                         'subject': self.subject,
                         'description': self.description,
                         'date': datetime.today().strftime('%Y-%m-%d'),
                         'items_manifest': manifest,
                         'items_ref': items_ref,
                         'identifier': random.choice(range(0, 10000))
                         }

        # {$identifier} {$title} {$creator} {$publisher} {$subject}
        # {$description} {$date} {$items_manifest} {$items_ref}
        html_data = CONTENTS_OPF_STR.format(template_data['identifier'],
                                            template_data['title'],
                                            template_data['creator'],
                                            template_data['publisher'],
                                            template_data['subject'],
                                            template_data['description'],
                                            template_data['date'],
                                            template_data['items_manifest'],
                                            template_data['items_ref'])

        self.write_file(filename, html_data)

    def create_ncx(self):
        """
        Use templates/nav-contents_ncx.template to format nav-contents.ncx
        """

        filename = self.book_directory + 'nav-contents.ncx'
        sections = ''
        section_count = 0

        for subscription in self.data:

            if subscription['items']:
                section_first = subscription['items'][0]['id']
            else:
                break

            articles = ''
            for item in subscription['items']:
                # {$id} {$title} {$id} {$description} {$author}
                article = ARTICLE_NCX_STR.format(item['id'],
                                                 item['title'],
                                                 item['id'],
                                                 self.
                                                 get_description(item['content']),
                                                 self.creator)
                articles = articles + article + '\n'

            # {$section_id} {$section_title} {$section_first} {$articles}
            section = SECTION_NCX_STR.format('section-' + str(section_count),
                                         subscription['title'],
                                         section_first,
                                         articles)
            section_count = section_count + 1
            sections = sections + section

        # {$title} {$creator} {$sections}
        nc_content = NAV_CONTENTS_NCX_STR.format(self.title,
                                                 self.creator,
                                                 sections)

        self.write_file(filename, nc_content)

    def create_mobi(self):
        """
        Uses (not given) bin/kindlegen to create mobi file
        """

        try:
            generate = os.path.dirname(os.path.realpath(__file__))\
                + '/bin/kindlegen -c2 '\
                + self.book_directory\
                + 'content.opf -o '\
                + self.filename + '.mobi'
            output = subprocess.call(generate, shell=True)
            if output > 1:
                raise Exception('Error creating .mobi file!')
            return self.filename + '.mobi'

        except Exception as e:
            print(e)
            return None

    def delete_temp_files(self):
        """
        Remove temp files
        """

        try:
            filelist = []
            filelist = filelist + glob.glob(self.book_directory + '*.html')
            filelist = filelist + glob.glob(self.book_directory + '*.opf')
            filelist = filelist + glob.glob(self.book_directory + '*.ncx')
            filelist = filelist + glob.glob(str(self.book_directory + 'data/') + '*.json')

            print('Deleting')
            for f in filelist:
                os.remove(f)

            return True

        except:
            print('Error deleting temp files!')
            return False

    def write_file(self, filename, content):
        """
        Write content to filename
        """

        file = open(filename, 'w+')
        file.write(content)

    def get_description(self, description):
        """
        Description is a reduced version of content
        """

        description = self.strip_tags(description)
        description = description.replace('\n', ' ')
        description = description.replace('  ', ' ')
        description = description.replace('        ', ' ')
        description = description.replace('>', '')
        description = description.replace('<', '')
        description = description[:500]

        return description

    def strip_tags(self, txt):
        """
        Just strip tags
        """

        return re.sub(r'<[^>]*?>', '', txt)

    def remove_empty_subscriptions(self):
        """
        Removes any subscription with no items
        """

        clean_data = []
        for subscription in self.data:
            if len(subscription['items']) == 0:
                continue
            clean_data.append(subscription)

        if len(clean_data) == 0:
            raise Exception("You don't have any unread feeds!")
        else:
            self.data = clean_data

if __name__ == '__main__':
    # For production DATA_FOLDER must be 'temp/data'
    DATA_FOLDER = 'data-templates'

    try:
        with open(DATA_FOLDER + '/metadata.json') as metadata_file:
            metadata = json.load(metadata_file)
    except:
        print('Error to open metadata.json')
        sys.exit()

    try:
        with open(DATA_FOLDER + '/content.json') as content_file:
            content = json.load(content_file)
    except:
        print('Error to open content.json')
        sys.exit()

    periodical = Periodical(metadata)
    periodical.set_content(content)
