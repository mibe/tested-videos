#!/usr/bin/env python

"""Listing video URLs of stories on tested.com.

Copyright: (C) 2014 Michael Bemmerl
License: MIT License (see LICENSE.txt)

Requirements:
- Python (well, obviously ;-)

Tested with Python 2.7.6
"""

import os.path
import feedparser
from lxml import html
from lxml.cssselect import CSSSelector
import urllib

class TestedVideos(object):
    YOUTUBE_REGEX = '[a-zA-Z0-9_-]{11}'
    VIMEO_REGEX = ''

    def load_feed_from(self, location):
        self.feed = feedparser.parse(location)

    def process_entries(self):
        self.process_entry(self.feed.entries[0])
        #for entry in self.feed.entries:
         #   self.process_entry(entry)
            
    def process_entry(self, entry):
        self.get_entry_page(entry)
        
    def get_entry_page(self, entry):
        root = html.parse(entry.link).getroot()
        elements = root.cssselect('div.embed-type-video iframe')
        
        for element in elements:
            result = self.analyze_url(element.get('src'))
            
    def analyze_url(self, url):
        print urllib.unquote_plus(url)
        
tv = TestedVideos()

if os.path.isfile('feed.xml'):
    tv.load_feed_from('feed.xml')
else:
    tv.load_feed_from('http://www.tested.com/feeds/')

tv.process_entries()
    