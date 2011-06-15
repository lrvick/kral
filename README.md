# Kral #

<http://github.com/lrvick/kral>

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

A running service capable of acting as a task management backend.

Currently supported backends are:

Redis, Memcached, MongoDB, Beanstalk, CouchDB, RabbitMQ and ActiveMQ

## Usage / Installation ##

### Install dependencies

```shell

pip install -r requirements.txt


```

### Start krald

```shell

python krald.py localhost 8080

```

### Collect data with kral.collect()

From here you can connect to your backend with kral.connect() and start 
using the kral.collect() generator to collect data within your appliction.

Example that outputs the latest social data on "android"

```python

import kral

// connect to krald
connection = kral.connect('localhost',8080) 

// print live data on 'android'
for item in connection.collect('android'):
    print "%s | %s" % (item.service,item.text)

```

## Notes ##

Many more features coming soon as this project is under active development.

This is by no means production-ready code. Do not actually use it in
production unless you wish to be eaten by a grue.

Questions/Comments? Please check us out on IRC via irc://udderweb.com/#uw
