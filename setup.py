from setuptools import setup

setup(name='kp3',
      version='0.4',
      description='A kindle periodical util writen in python 3 for generating kindle .mobi files in periodical style.',
      url='https://github.com/andresmlna/kindle-periodical',
      author='Andrés Molina',
      author_email='andresmlna@users.noreply.github.com',
      license='GPL-V3',
      packages=['kp3'],
      package_data={'kp3': ['images/*', 'templates/*']},
      install_requires=['beautifulsoup4','feedparser'],
      zip_safe=False
      )
