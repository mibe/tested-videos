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
from collections import OrderedDict
from unidecode import unidecode
import sys

parser = argparse.ArgumentParser(description="List video URLs of stories on tested.com.")
parser.add_argument('--html', action='store_true', help="HTML output instead of plain text")
parser.add_argument('--file', help="Load feed from a file instead from the Internet")
parser.add_argument('--hide-empty', action='store_true', help="Hide stories without videos")
parser.add_argument('--ssl', action='store_true', help="Use HTTPS for URLs")

args = parser.parse_args()

class TestedVideos(object):
    
    def __init__(self, ssl=False):
        self.ssl = ssl
        self.result = OrderedDict()
        self.providers = dict()

        self.providers['youtube'] = dict()
        self.providers['youtube']['pattern'] = re.compile('[a-zA-Z0-9_-]{11}')
        self.providers['youtube']['group'] = 0
        self.providers['youtube']['template'] = '{0}://youtu.be/{1}'

        self.providers['vimeo'] = dict()
        self.providers['vimeo']['pattern'] = re.compile('vimeo.+?/(\d+)')
        self.providers['vimeo']['group'] = 1
        self.providers['vimeo']['template'] = '{0}://vimeo.com/{1}'

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
            data = self.analyze_url(url)
            if data:
                result.append(data)
            
        self.result[entry.title] = result
            
    def analyze_url(self, url):
        url = urllib.unquote_plus(url)
        
        for name in self.providers.keys():
            provider = self.providers[name]
            match = provider['pattern'].search(url)
            if match:
                result = dict()
                result['provider'] = name
                result['token'] = match.group(provider['group'])
                return result
                
        return None
        
    def print_plain(self, hide_empty=False):
        print "List generated on {0}:\n".format(datetime.now())
        
        for key in self.result:
            if not hide_empty or self.result[key]:
                # Transliterate to ASCII for stupid Windows console:
                if sys.platform == 'win32' and sys.stdout.encoding == 'cp850':
                    print unidecode(key)
                else:
                    print key
                    
                for item in self.result[key]:
                    url = self.build_video_url(item['provider'], item['token'])
                    print "  " + url
                    
                print "-" * 80

    def print_html(self, hide_empty=False):
        html = '<!DOCTYPE html><html><head><title>tested.com videos</title></head><body>'
        html = html + '<p>List generated on {0}'.format(datetime.now())
        
        for key in self.result:
            if not hide_empty or self.result[key]:
                title = key
                # Transliterate to ASCII for stupid Windows console:
                if sys.platform == 'win32' and sys.stdout.encoding == 'cp850':
                    title = unidecode(key)

                html = html + '<h3>{0}</h3><ul>'.format(title)
                for item in self.result[key]:
                    url = self.build_video_url(item['provider'], item['token'])
                    html = html + '<li><a href=\"{0}\">{0}</a></li>'.format(url)
                html = html + '</ul>'
        
        html = html + '</body></html>'
        print html
        
    def build_video_url(self, provider, token):
        if provider in self.providers:
            scheme = 'http'
            if self.ssl:
                scheme += 's'
                
            return self.providers[provider]['template'].format(scheme, token)
        else:
            return None

tv = TestedVideos(args.ssl)

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
