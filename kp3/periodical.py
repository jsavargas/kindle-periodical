# KINDLE-PERIODICAL for Python 3
# This is a fork from vncprado/kindle-periodical for Python 2.
# https://github.com/vncprado/kindle-periodical

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


# Class that implements Kindle periodical file generation.
class Periodical:
    IMAGE_COVER = os.path.dirname(os.path.realpath(__file__)) + '/images/cover.jpg'
    IMAGE_MASTHEAD = os.path.dirname(os.path.realpath(__file__)) + '/images/masthead.jpg'
    BOOK_DIR_TEMP = os.path.dirname(os.path.realpath(__file__)) + '~/temp'
    KINDLEGEN_PATH = '~/kindlegen'

    def set_metadata(self, data):
        self.__title = data['title']
        self.__creator = data['creator']
        self.__publisher = data['publisher']
        self.__subject = data['subject']
        self.__description = data['description']
        self.__filename = data['filename'] + '_' + datetime.today().strftime('%Y-%m-%d')

    # If temp folder not exist, will make one.
    # folder - string - Path folder for make a folder on file system.
    def __make_folder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Correcting any wrong encoding
    # input - string - Word for encoding check.
    def __fix_encoding(self, input):
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

    # Decoding HTML.
    # html - string - HTML data.
    def __html_decoding(self, html):
        try:
            return json.loads(html)
        except Exception as e:
            print(e)
            return html

    # Create/modify description, date, title and content from items in subscriptions.
    # data - list - List with subscriptions data.
    def __setup_data(self, data):
        data = self.__fix_encoding(data)
        for subscription in data:
            new_subscription = []
            for item in subscription['items']:
                if 'content' not in list(item.keys()):
                    del item
                    continue
                else:
                    item['content'] = self.__html_decoding(item['content'])

                item['description'] = self.__get_description(item['content'])

                if 'published' in list(item.keys()) and isinstance(item['published'], int):
                    item['date'] = datetime.fromtimestamp(item['published']).strftime('%Y-%m-%d')
                else:
                    item['date'] = datetime.today().strftime('%Y-%m-%d')

                if 'title' in list(item.keys()) and not isinstance(item['title'], str):
                    del item
                    continue
                elif len(item['title']) == 0:
                    item['title'] = self.__get_description(item['content'])[:35]
                else:
                    item['title'] = item['title']

                if 'author' not in list(item.keys()) or not isinstance(item['author'], str) or len(item['author']) == 0:
                    item['author'] = ' '

                # Assign a unique ID for files generation on temp folder.
                item['id'] = str(uuid.uuid4())

                new_subscription.append(item)
            subscription['items'] = new_subscription

            # Assign a unique ID for files generation on temp folder.
            subscription['id'] = str(uuid.uuid4())

        self.__data = data

        self.__remove_empty_subscriptions()

    # Download and store images from articles.
    # item_id - string - Unique article ID.
    # html_content - string -  HTML data.
    def __articles_images(self, item_id, html_content):
        html_code = BeautifulSoup(html_content, 'lxml')
        images_list = html_code.find_all('img')

        # If images exists.
        if len(images_list) > 0:
            img_count = 0
            # If temp folder not exists, will create.
            if not os.path.exists(self.BOOK_DIR_TEMP + '/'+ item_id):
                os.makedirs(self.BOOK_DIR_TEMP + '/' + item_id)

            for img in images_list:
                img_count += 1

                try:
                    # Only for URL without 'http:'
                    if str(img.attrs['src'])[:2] == '//':
                        img.attrs['src'] = 'http:' + img.attrs['src']
                    # Download image from <img> URL HTML tag.
                    response = urllib.request.urlopen(img.attrs['src'])
                    img_data = response.read()
                    # Check image type.
                    img_type = imghdr.what('', h=img_data)

                    # If not image, remove <img> tag from HTML code.
                    if isinstance(img_type, type(None)):
                        html_code.img.extract()
                    else:
                        # Store image in temp folder.
                        img_name = "image_{0}.{1}".format(img_count, img_type)
                        img_full_name = self.BOOK_DIR_TEMP + '/' + item_id + '/' + img_name
                        img_file = open(img_full_name, "wb+")
                        img_file.write(img_data)
                        img_file.close()

                        # Sets a new <img> tag source from downloaded image.
                        img.attrs['src'] = item_id + '/' + img_name
                except Exception as e:
                    print(e)
                    # Remove <img> tag from HTML code.
                    html_code.img.extract()

            # Extract <body> tag from HTML code.
            html_article = html_code.findChild('body').findChildren()

            return html_article[0]
        else:
            return html_content

    # Create HTML code for a article.
    # Use templates/article.template file to format html article creating their files.
    def __create_articles(self):
       for subscription in self.__data:
            for item in subscription['items']:
                filename = self.BOOK_DIR_TEMP + '/' + item['id'] + '.html'
                if item['published']:
                    author = item['author']
                    description = item['description']
                    date = item['date']
                    title = item['title']
                    content = self.__articles_images(item['id'], item['content'])

                # {$title} {$author} {$date} {$description} {$title} {$content}
                html_data = ARTICLE_STR.format(title,
                                               author,
                                               date,
                                               description,
                                               title,
                                               content)

                self.__write_file(filename, html_data)

    # Use templates/contents.template file to format content.html file.
    def __create_contents(self):
        filename = self.BOOK_DIR_TEMP + '/contents.html'
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

    # Use templates/content_opf.template to format content.opf file
    def __create_opf(self):
        manifest = ''
        items_ref = ''
        filename = self.BOOK_DIR_TEMP + '/content.opf'

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
                         'identifier': random.choice(list(range(0, 10000)))}

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

    # Use templates/nav-contents_ncx.template to format nav-contents.ncx
    def __create_ncx(self):
        sections = ''
        section_count = 0
        play_order_count = 1
        filename = self.BOOK_DIR_TEMP + '/nav-contents.ncx'

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

    # Uses (not given) bin/kindlegen to create mobi file.
    def __create_mobi(self):
        try:
            generate = self.KINDLEGEN_PATH\
                + '/kindlegen -c2 '\
                + self.BOOK_DIR_TEMP\
                + '/content.opf -o '\
                + self.__filename + '.mobi'
            output = subprocess.call(generate, shell=True)

            # Raise a exception if has produced a error generating *.mobi file.
            if output > 1:
                raise Exception('Error creating .mobi file!')

            return self.BOOK_DIR_TEMP + '/' + self.__filename + '.mobi'

        except Exception as e:
            print(e)
            return None

    # Remove temp files.
    def __delete_temp_files(self):
        try:
            file_list = []
            folder_list = []
            file_list = file_list + glob.glob(self.BOOK_DIR_TEMP + '/' + '*.html')
            file_list = file_list + glob.glob(self.BOOK_DIR_TEMP + '/' + '*.opf')
            file_list = file_list + glob.glob(self.BOOK_DIR_TEMP + '/' + '*.ncx')

            for entry in os.scandir(self.BOOK_DIR_TEMP):
                if not entry.is_file():
                    folder_list.append(entry.name)

            print('\nDeleting...')

            for f in file_list:
                os.remove(f)
            for d in folder_list:
                shutil.rmtree(self.BOOK_DIR_TEMP + '/' + d)

            return True

        except Exception as e:
            print(e)
            print('Error deleting temp files!')
            return False

    # Write content to filename.
    # filename - string - Filename to write.
    # content - string - Content to write.
    def __write_file(self, filename, content):
        file = open(filename, 'w+', encoding='utf-8')
        file.write(content)

    # Get description text from article, is a reduced version of content.
    # text - string - Text to extract a description.
    def __get_description(self, text):
        text = self.__strip_tags(text)
        text = text.replace('\n', ' ')
        text = text.replace('  ', ' ')
        text = text.replace('        ', ' ')
        text = text.replace('>', '')
        text = text.replace('<', '')
        text = text[:650]

        if text == '':
            text = ' '

        return text

    # Just strip tags.
    # text - string - Text to strip.
    def __strip_tags(self, text):
        return re.sub(r'<[^>]*?>', '', text)

    # Removes any subscription with no items.
    def __remove_empty_subscriptions(self):
        clean_data = []
        for subscription in self.__data:
            if len(subscription['items']) == 0:
                continue
            clean_data.append(subscription)

        if len(clean_data) == 0:
            raise Exception("You don't have any unread feeds!")
        else:
            self.__data = clean_data

    # Function that creates all necessary files with provided data.
    def set_content(self, data):
        print('\n')
        self.__make_folder(self.BOOK_DIR_TEMP)
        self.__setup_data(data)
        print('Setup Data OK')
        self.__create_articles()
        print('Articles OK')
        self.__create_contents()
        print('Contents OK')
        self.__create_opf()
        print('OPF OK')
        self.__create_ncx()
        print('NCX OK')

    # Main function for create kindle periodical.
    def make_periodical(self):
        created_file = self.__create_mobi()
        print('\nBook', created_file, 'OK!')

        deleted = self.__delete_temp_files()
        if deleted:
            print("Temp files removed!\n")

        # Return full path for *.mobi file created.
        return created_file

