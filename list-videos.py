#!/usr/bin/env python

"""List video URLs of stories on tested.com.

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
import argparse

parser = argparse.ArgumentParser(description="List video URLs of stories on tested.com.")
parser.add_argument('--html', action='store_true', help="HTML output instead of plain text")
parser.add_argument('--file', help="Load feed from a file instead from the Internet")
parser.add_argument('--hide-empty', action='store_true', help="Hide stories without videos")

args = parser.parse_args()

class TestedVideos(object):
    
    def __init__(self):
        self.patterns = [re.compile('[a-zA-Z0-9_-]{11}')]
        self.result = dict()

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
            
        self.result[entry.title] = result
            
    def analyze_url(self, url):
        url = urllib.unquote_plus(url)
        
        result = None
        for pattern in self.patterns:
            match =  pattern.search(url)
            if match:
                return match.group(0)
                
        return result
        
    def print_plain(self, hide_empty=False):
        print "List generated on {0}:\n".format(datetime.now())
        
        for key in self.result:
            if not hide_empty or self.result[key]:
                print key
                for item in self.result[key]:
                    print "  https://youtu.be/{0}".format(item)
                print "-" * 80

    def print_html(self, hide_empty=False):
        html = '<!DOCTYPE html><html><head><title>tested.com videos</title></head><body>'
        html = html + '<p>List generated on {0}'.format(datetime.now())
        
        for key in self.result:
            if not hide_empty or self.result[key]:
                html = html + '<h3>' + key + '</h3><ul>'
                for item in self.result[key]:
                    html = html + '<li><a href=\"https://youtu.be/{0}\">https://youtu.be/{0}</a></li>'.format(item)
                html = html + '</ul>'
        
        html = html + '</body></html>'
        print html

tv = TestedVideos()

if not args.html:
    print "Loading feed..."

if args.file and os.path.isfile(args.file):
    tv.load_feed_from(args.file)
else:
    tv.load_feed_from('http://www.tested.com/feeds/')
    
tv.process_entries()

if args.html:
    tv.print_html(args.hide_empty)
else:
    tv.print_plain(args.hide_empty)
