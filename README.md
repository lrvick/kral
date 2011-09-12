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

## Requirements ##

Celery is used for task management within kral, and at a minimum it requires
a key/value store to keep track of the running tasks, and a backend to stash
results as it goes.

Redis fufills both of these requirements, and for means of simple deployment,
is the default.

For production use however, AMQP setups like RabbitMQ will take a far larger
beating.

## Usage / Installation ##

1. Install dependencies

    ```pip install -r requirements.txt```

2. Edit settings.py to suit your needs

3. Edit celeryconfig.py to suit your needs

4. Start Celery

    ```celeryd --purge -l INFO```

5.  Collect data with kral.stream()

From here you can start using the kral.collect() generator to collect data 
within your appliction.

Example that outputs the latest social data on "android" and "bitcoin"

```python

import kral

for item in kral.stream(['android','bitcoin']):
    print "%s | %s" % (item.service,item.text)

```

## Notes ##

Many more features coming soon as this project is under active development.

This is by no means production-ready code. Do not actually use it in
production unless you wish to be eaten by a grue.

Questions/Comments? Please check us out on IRC via irc://udderweb.com/#uw
