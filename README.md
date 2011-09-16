# Kral #

<http://github.com/Tawlk/kral>

## About ##

kral (pronounced: "crawl") is a python library intended to be a flexible solution
for retreiving live streaming data from a variety of social network apis on given
keyword(s), and yeilding the retreived data in a unified format.

## Current Features ##

  * Ability to harvest user information, and posts from Twitter, Facebook, Buzz,
    Identica, Youtube, Flickr, Wordpress
  * Ability to expand all short-urls into full real URLs.
  * Ability to track number of mentions of a given URL across multiple networks.
  * Modular design. Easily add or disable plugins for different social networks.

## Usage / Installation ##

1. Install dependencies

    ```pip install -r requirements.txt```

2. Include settings and set any credentials for services that require them

    ```python
    include kral.settings
    kral.settings['TWITTER_USER'] = 'youruser'
    kral.settings['TWITTER_USER'] = 'your_pass'
    kral.settings['BUZZ_API_KEY'] = 'your_key'
    kral.settings['FACEBOOK_API_KEY'] = 'your_key'
    kral.settings['FLICKR_API_KEY'] = 'your_key'
    ```

3.  Collect data with kral.stream()

From here you can start using the kral.stream() generator to collect data
within your appliction.

Example that outputs the latest social data on "android" and "bitcoin" across
all available networks.

```python

import kral

for item in kral.stream(['android','bitcoin']):
    print "%s | %s" % (item.service,item.text)

```

Example that outputs the latest social data on "obama" using only twitter.

```python

import kral

for item in kral.stream('obama','twitter'):
    print "%s | %s" % (item.service,item.text)

```

## Notes ##

Many more features coming soon as this project is under active development.

This is by no means production-ready code. Do not actually use it in
production unless you wish to be eaten by a grue.

Questions/Comments? Please check us out on IRC via irc://udderweb.com/#uw
