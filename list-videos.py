#!/usr/bin/env python

"""List video URLs in stories on tested.com. The official RSS feed is used for that.

Copyright: (C) 2014 Michael Bemmerl
License: MIT License (see LICENSE.txt)

Requirements:
- Python >= 2.7 (well, obviously ;-)
- feedparser (https://pypi.python.org/pypi/feedparser)
- lxml (https://pypi.python.org/pypi/lxml)
- Unidecode (https://pypi.python.org/pypi/Unidecode)

Tested with Python 2.7.6, feedparser 5.1.3, lxml 3.3.1 and Unidecode 0.04.14
"""

import os
import feedparser
from lxml import html
import urllib
import re
from datetime import datetime
import argparse
from collections import OrderedDict
from unidecode import unidecode
import sys

parser = argparse.ArgumentParser(description="List video URLs in stories on tested.com.")
parser.add_argument('--html', action='store_true', help="HTML output instead of plain text")
parser.add_argument('--file', help="Load feed from a file instead from the Internet")
parser.add_argument('--hide-empty', action='store_true', help="Hide stories without videos")
parser.add_argument('--ssl', action='store_true', help="Use HTTPS for URLs")
parser.add_argument('--reverse', action='store_true', help="Display the stories in reversed order")
parser.add_argument('--only-new', action='store_true',
                    help="Only display stories which were published since last invoke")

args = parser.parse_args()


class TestedVideos(object):
    # File, in which the date and time the last time this class was active is saved to.
    LASTRUN_FILE = 'lastrun'
    
    def __init__(self, ssl=False, reverse=False, only_new=False):
        self.ssl = ssl
        self.reverse = reverse
        self.only_new = only_new
        
        self.lastrun = datetime.min
        # Check if the lastrun file is existing. If yes, try to parse its contents.
        if os.path.isfile(self.LASTRUN_FILE):
            try:
                with open(self.LASTRUN_FILE, 'r') as file:
                    self.lastrun = datetime.strptime(file.readline(), '%c')
            except:
                os.unlink(self.LASTRUN_FILE)
        
        self.result = OrderedDict()
        self.providers = dict()

        # Generate the list of supported video providers.
        self.providers['youtube'] = dict()
        self.providers['youtube']['pattern'] = re.compile('[a-zA-Z0-9_-]{11}')
        self.providers['youtube']['group'] = 0
        self.providers['youtube']['template'] = '{0}://youtu.be/{1}'

        self.providers['vimeo'] = dict()
        self.providers['vimeo']['pattern'] = re.compile('vimeo.+?/(\d+)')
        self.providers['vimeo']['group'] = 1
        self.providers['vimeo']['template'] = '{0}://vimeo.com/{1}'
        
    def __del__(self):
        # Save the current date & time to the lastrun file. This is used for displaying
        # feed entries which were published after this date.
        with open(self.LASTRUN_FILE, 'w') as lastrun:
            lastrun.write(datetime.now().strftime('%c'))

    def load_feed_from(self, location):
        """Loads the feed. location can be a URL or path to a file."""
        self.feed = feedparser.parse(location)

    def process_entries(self):
        """Start processing all feed entries.
        
        This must be called before calling any print_*-methods."""
        # Reverse the feed entries when this is desired.
        if self.reverse:
            self.feed.entries.reverse()
        
        for entry in self.feed.entries:
            self.process_entry(entry)
           
    def process_entry(self, entry):
        """Process a single feed entry."""
        # Nothing to do here if the published item date is older than the last time
        # this class was active. This does of course only apply if this behavior is desired.
        if self.only_new and datetime(*entry.published_parsed[:6]) < self.lastrun:
            return
            
        # Filter content for "Premium" subscribers.
        if "/premium/" in entry.link:
            return
            
        result = list()
        
        root = html.parse(entry.link).getroot()
        iframes = root.cssselect('div.embed-type-video iframe')
        divs = root.cssselect('div.embed-type-video div')
        
        # As of writing this, the videos on tested.com are embedded via an iframe.
        # This HTML element has to be found. This element can occur multiple times.
        for element in iframes:
            url = element.get('src')
            data = self.analyze_url(url)
            if data:
                result.append(data)
                
        # Well, as of writing THIS (August 2014), they also use the YouTube iframe API.
        # This sucks a bit...
        for element in divs:
            id = element.get('id')
            className = element.get('class')
            if id:
                match = re.match('player-([a-zA-Z0-9_-]{11})', id)
                if match:
                    entity = dict()
                    entity['provider'] = 'youtube'
                    entity['token'] = match.group(1)
                    result.append(entity)
            elif className:
                entity = dict()
                entity['provider'] = 'youtube'
                entity['token'] = element.get('data-video-id');
                result.append(entity)
                
        self.result[entry.title] = result
            
    def analyze_url(self, url):
        """Tries to get the video token from a specified URL."""
        # Sometimes the video URLs are urlencoded. So decode it...
        url = urllib.unquote_plus(url)
        
        # Check for every provider if the regex is matching on the URL.
        # If yes, return a dictionary containing the provider and the video token.
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
        """Display the found story titles and the containing video URLs on stdout."""
        if not self.result:
            print "No stories or no new stories found."
            return
            
        print "List generated on {0}:\n".format(datetime.now())
        
        for key in self.result:
            # Skip the story if it does not contain any video URLs, but only if this
            # behavior is desired.
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
        """Display the found story titles and the containing video URLs in HTML format."""
        html = '<!DOCTYPE html><html><head><title>tested.com videos</title></head><body>'
        html = html + '<p>List generated on {0}'.format(datetime.now())
        
        for key in self.result:
            # Skip the story if it does not contain any video URLs, but only if this
            # behavior is desired.
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
        """Builds a URL to the video provider by specifying the provider and the video token."""
        if provider in self.providers:
            scheme = 'http'
            if self.ssl:
                scheme += 's'
                
            return self.providers[provider]['template'].format(scheme, token)
        else:
            return None

# Instantiate class with arguments from the command line
tv = TestedVideos(args.ssl, args.reverse, args.only_new)

# Don't print the "please wait" message when in HTML mode
if not args.html:
    print "Loading feed..."

# Use the feed file if it is existing. Use the official feed URL otherwise.
if args.file and os.path.isfile(args.file):
    tv.load_feed_from(args.file)
else:
    tv.load_feed_from('http://www.tested.com/feeds/')

# Process all feed entries
tv.process_entries()

# Choose between the output modes.
if args.html:
    tv.print_html(args.hide_empty)
else:
    tv.print_plain(args.hide_empty)
