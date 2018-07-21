tested-videos
=============

A tool for listing video URLs in stories on tested.com.

This is done by downloading and parsing the official tested.com RSS feed.
Every feed entry corresponds to a story. This story is in turn fetched and
its content analyzed for videos.

Currently the following video providers are supported:
* YouTube
* Vimeo

Usage
-----

    usage: list-videos.py [-h] [--html] [--file FILE] [--hide-empty] [--reverse]
                          [--only-new]

    List video URLs of stories on tested.com.

    optional arguments:
      -h, --help    show this help message and exit
      --html        HTML output instead of plain text
      --file FILE   Load feed from a file instead from the Internet
      --hide-empty  Hide stories without videos
      --reverse     Display the stories in reversed order
      --only-new    Only display stories which were published since last invoke

Example
-----
Command line:

    list-videos.py --hide-empty --only-new --reverse

Output:

    Loading feed...
    List generated on 2014-03-30 00:56:56.043000:

    A Landmark Episode of This Is Only a Test - 3/27/2014
      http://youtu.be/vWtfHiQx50U
    --------------------------------------------------------------------------------

    The Motion Picture Camera: Past, Present and Future
      http://vimeo.com/88675290
    --------------------------------------------------------------------------------

    Tested In-Depth: Sony a7 Full-Frame Mirrorless Camera
      http://youtu.be/zPd2OiDjI_c
    --------------------------------------------------------------------------------

    Makerbot Mystery Build: Failure is an Option
      http://youtu.be/bf_43POmSFE
    --------------------------------------------------------------------------------

    Tested Mailbag: Slamming Tim Tams and 3D-Printed Wonders
      http://youtu.be/jclNJThsO0E
    --------------------------------------------------------------------------------

Requirements
-----

* Python >= 2.7.9 (well, obviously ;-)
* feedparser (https://pypi.python.org/pypi/feedparser)
* lxml (https://pypi.python.org/pypi/lxml)
* Unidecode (https://pypi.python.org/pypi/Unidecode)

Tested with Python 2.7.15, feedparser 5.1.3, lxml 3.3.1 and Unidecode 0.04.14

License
-----

MIT License (see LICENSE.txt)
