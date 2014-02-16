#!/usr/bin/env python

"""Listing video URLs of stories on tested.com.

Copyright: (C) 2014 Michael Bemmerl
License: MIT License (see LICENSE.txt)

Requirements:
- Python (well, obviously ;-)

Tested with Python 2.7.6
"""

import os
import feedparser
from lxml import html
from lxml.cssselect import CSSSelector
import urllib
import re
from datetime import datetime

class TestedVideos(object):
    
    def __init__(self):
        self.patterns = [re.compile('[a-zA-Z0-9_-]{11}')]

    def load_feed_from(self, location):
        self.feed = feedparser.parse(location)

    def process_entries(self):
        for entry in self.feed.entries:
            self.process_entry(entry)
            
    def process_entry(self, entry):
        root = html.parse(entry.link).getroot()
        elements = root.cssselect('div.embed-type-video iframe')
        
        result = list()
        for element in elements:
            url = element.get('src')
            id = self.analyze_url(url)
            if id:
                result.append(id)
            
        print entry.title
        for item in result:
            print "  https://youtu.be/{0}".format(item)
        print "-" * 80
            
    def analyze_url(self, url):
        url = urllib.unquote_plus(url)
        
        result = None
        for pattern in self.patterns:
            match =  pattern.search(url)
            if match:
                return match.group(0)
                
        return result
        
tv = TestedVideos()

if os.path.isfile('feed.xml'):
    tv.load_feed_from('feed.xml')
else:
    tv.load_feed_from('http://www.tested.com/feeds/')

print "List generated on {0}:\n".format(datetime.now())

tv.process_entries()
    