# -*- coding: utf-8 -*-

import os
import glob
import re
import json
import uuid
import shutil
import imghdr
import random
import subprocess
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup
from .templates import *

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


class Periodical:
    """
    Class that implements Kindle periodical file generation
    """

    IMAGE_COVER = os.path.abspath(os.path.join(os.path.curdir)) + '/kindle/images/cover.jpg'
    IMAGE_MASTHEAD = os.path.abspath(os.path.join(os.path.curdir)) + '/kindle/images/masthead.jpg'
    BOOK_DIR_TEMP = os.path.abspath(os.path.join(os.path.curdir)) + '/temp/'

    def set_metadata(self, data):
        self.__title = data['title']
        self.__creator = data['creator']
        self.__publisher = data['publisher']
        self.__subject = data['subject']
        self.__description = data['description']
        self.__filename = data['filename'] + '_' + datetime.today().strftime('%Y-%m-%d')

    def __fix_encoding(self, input):
        """
        Correcting any wrong encoding
        """

        if isinstance(input, dict):
            return {self.__fix_encoding(key):
                    self.__fix_encoding(value) for key,
                    value in input.items()}
        elif isinstance(input, list):
            return [self.__fix_encoding(element) for element in input]
        if isinstance(input, str):
            return input.encode('ascii', 'xmlcharrefreplace').decode('utf-8')
        else:
            return input

    def __html_decoding(self, html):
        try:
            return json.loads(html)
        except:
            return html

    def __setup_data(self, data):
        """
        Create/modify description, date, title and content from items
        in subscriptions
        """

        data = self.__fix_encoding(data)
        for subscription in data:
            for item in subscription['items']:
                if item['published']:
                    if not 'content' in list(item.keys()):
                        item['content'] = ' '
                    else:
                        item['content'] = self.__html_decoding(item['content'])

                    item['description'] = self.__get_description(item['content'])

                    item['date'] = datetime.fromtimestamp(
                        item['published'] / 1000).strftime('%d/%m/%Y')

                    if 'title' in list(item.keys()):
                        item['title'] = item['title']
                    else:
                        item['title'] = item['description'][:15]\
                            + ' - ' + item['date']

                    if not 'author' in list(item.keys()):
                        item['author'] = ' '

                    if item['author'] == '':
                        item['author'] = ' '

                    item['id'] = str(uuid.uuid4())

            subscription['id'] = str(uuid.uuid4())

        self.__data = data

        self.__remove_empty_subscriptions()

    def __content_with_images(self, item_id, html_content):
        html_code = BeautifulSoup(html_content)
        images_list = html_code.find_all('img')

        if len(images_list) > 0:
            img_count = 0
            if not os.path.exists(self.BOOK_DIR_TEMP + item_id):
                os.makedirs(self.BOOK_DIR_TEMP + item_id)

            for img in images_list:
                img_count += 1

                try:
                    response = urllib.request.urlopen(img.attrs['src'])
                    img_data = response.read()

                    img_type = imghdr.what('', h=img_data)

                    if isinstance(img_type, type(None)):
                        html_code.img.extract()
                    else:
                        img_name = "image_{0}.{1}".format(img_count, img_type)
                        img_full_name = self.BOOK_DIR_TEMP + item_id + '/' + img_name
                        img_file = open(img_full_name, "wb+")
                        img_file.write(img_data)
                        img_file.close()

                        img.attrs['src'] = item_id + '/' + img_name
                except:
                    html_code.img.extract()

            html_article = html_code.findChild('body').findChildren()

            return html_article[0]
        else:
            return html_content

    def __create_articles(self):
        """
        Use templates/article.template file to format html article
        creating their files
        """

        for subscription in self.__data:
            for item in subscription['items']:
                filename = self.BOOK_DIR_TEMP + item['id'] + '.html'
                if item['published']:
                    description = item['description']
                    date = item['date']
                    title = item['title']
                    content = self.__content_with_images(item['id'], item['content'])
                # {$title} {$creator} {$description} {$title} {$content}
                html_data = ARTICLE_STR.format(title,
                                               subscription['title'],
                                               description,
                                               title,
                                               content,
                                               )

                self.__write_file(filename, html_data)

    def __create_contents(self):
        """
        Use templates/contents.template file to format content.html file
        """

        filename = self.BOOK_DIR_TEMP + 'contents.html'
        sections = ''
        for subscription in self.__data:
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

        self.__write_file(filename, html_data)

    def __create_opf(self):
        """
        Use templates/content_opf.template to format content.opf file
        """

        filename = self.BOOK_DIR_TEMP + 'content.opf'

        manifest = ''
        items_ref = ''

        for subscriptions in self.__data:
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

        template_data = {'title': self.__title,
                         'creator': self.__creator,
                         'publisher': self.__publisher,
                         'subject': self.__subject,
                         'description': self.__description,
                         'date': datetime.today().strftime('%Y-%m-%d'),
                         'cover': self.IMAGE_COVER,
                         'items_manifest': manifest,
                         'items_ref': items_ref,
                         'identifier': random.choice(list(range(0, 10000)))
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
                                            template_data['cover'],
                                            template_data['items_manifest'],
                                            template_data['items_ref'])

        self.__write_file(filename, html_data)

    def __create_ncx(self):
        """
        Use templates/nav-contents_ncx.template to format nav-contents.ncx
        """

        filename = self.BOOK_DIR_TEMP + 'nav-contents.ncx'
        sections = ''
        section_count = 0
        play_order_count = 1

        for subscription in self.__data:

            if subscription['items']:
                section_first = subscription['items'][0]['id']
            else:
                break

            articles = ''
            play_order_temp = play_order_count

            for item in subscription['items']:
                play_order_count += 1
                # {$id} {$title} {$id} {$description} {$author}
                article = ARTICLE_NCX_STR.format(play_order_count,
                                                 item['id'],
                                                 item['title'],
                                                 item['id'],
                                                 self.__get_description(item['content']),
                                                 item['author'])

                articles = articles + article + '\n'

            play_order_count += 1
            # {$section_id} {$section_title} {$section_first} {$articles}
            section = SECTION_NCX_STR.format(play_order_temp,
                                             'section-' + str(section_count),
                                             subscription['title'],
                                             section_first,
                                             articles)

            section_count += 1
            sections = sections + section

        # {$title} {$creator} {$sections}
        nc_content = NAV_CONTENTS_NCX_STR.format(self.__title,
                                                 self.__creator,
                                                 self.IMAGE_MASTHEAD,
                                                 sections)

        self.__write_file(filename, nc_content)

    def __create_mobi(self):
        """
        Uses (not given) bin/kindlegen to create mobi file
        """

        try:
            generate = os.path.dirname(os.path.realpath(__file__))\
                + '/bin/kindlegen -c2 '\
                + self.BOOK_DIR_TEMP\
                + 'content.opf -o '\
                + self.__filename + '.mobi'
            output = subprocess.call(generate, shell=True)
            if output > 1:
                raise Exception('Error creating .mobi file!')
            return self.BOOK_DIR_TEMP + self.__filename + '.mobi'

        except Exception as e:
            # print(e)
            return None

    def __delete_temp_files(self):
        """
        Remove temp files
        """

        try:
            file_list = []
            folder_list = []

            file_list = file_list + glob.glob(self.BOOK_DIR_TEMP + '*.html')
            file_list = file_list + glob.glob(self.BOOK_DIR_TEMP + '*.opf')
            file_list = file_list + glob.glob(self.BOOK_DIR_TEMP + '*.ncx')

            with os.scandir(self.BOOK_DIR_TEMP) as dir:
                for entry in dir:
                    if not entry.is_file():
                        folder_list.append(entry.name)

            # print('Deleting')
            for f in file_list:
                os.remove(f)
            for d in folder_list:
                shutil.rmtree(self.BOOK_DIR_TEMP + d)

            return True

        except:
            # print('Error deleting temp files!')
            return False

    def __write_file(self, filename, content):
        """
        Write content to filename
        """

        file = open(filename, 'w+')
        file.write(content)

    def __get_description(self, description):
        """
        Description is a reduced version of content
        """

        description = self.__strip_tags(description)
        description = description.replace('\n', ' ')
        description = description.replace('  ', ' ')
        description = description.replace('        ', ' ')
        description = description.replace('>', '')
        description = description.replace('<', '')
        description = description[:500]

        if description == '':
            description = ' '

        return description

    def __strip_tags(self, txt):
        """
        Just strip tags
        """

        return re.sub(r'<[^>]*?>', '', txt)

    def __remove_empty_subscriptions(self):
        """
        Removes any subscription with no items
        """

        clean_data = []
        for subscription in self.__data:
            if len(subscription['items']) == 0:
                continue
            clean_data.append(subscription)

        if len(clean_data) == 0:
            raise Exception("You don't have any unread feeds!")
        else:
            self.__data = clean_data

    def set_content(self, data):
        """
        Main function that creates all necessary files with provided data
        """

        self.__setup_data(data)
        # print('Setup Data OK')

        self.__create_articles()
        # print('Articles OK')

        self.__create_contents()
        # print('Contents OK')

        self.__create_opf()
        # print('OPF OK')

        self.__create_ncx()
        # print('NCX OK')

    def make_periodical(self):
        created_file = self.__create_mobi()
        # print('Book', created_file, 'OK!')

        deleted = self.__delete_temp_files()
        # if deleted:
            # print("Temp Files Removed!")

        return created_file

