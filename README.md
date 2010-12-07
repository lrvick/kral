# KRAL #

A social media crawling engine, built on Django. 

Aims to provide a framework for rapidly collect data from social networks
based on defined search criteria. Built to be a foundation for a wide 
range of social applications, to bring accountability to the way in which 
data is collected, and promote others to get involved to help us collect 
as much data as possible with the fewest resources.

## Current Features ##

  * Ability to harvest user information, and posts from Twitter and 
  * Ability to expand all short-urls into full real URLs.
  * Modular design. Easily add or disable plugins for different social networks.


## Configuration Options ##


### KRAL_PLUGINS ###

All plugins are enabled by default. To only enable certian plugins, list them in KRAL_PLUGINS as a list in settings.py

Example:

    KRAL_PLUGINS = ["Twitter", "Facebook"]    


### KRAL_SLOTS ###

Maximum number of query terms to collect data on at the same time

You could for instance, only allow a maximum of 10 queries to be followed at a time.

Example:

    KRAL_SLOTS = "10"


### KRAL_USERAGENT ###

Use KRAL_USERAGENT to masqurade as another browser

You could esaily use this to set all plugins to masqurade as Firefox.

Example:

    KRAL_USERAGENT = "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.7.6) Gecko/20050512 Firefox"

NOTE: Doing this might violate TOS on some services. Use at your own risk.



## Operating Kral from CLI ##


### Feeding queries to Kral ###

Before running Kral for the first time you must define at least one query term for it to collect data on.

You can add new queries at any time, even when kralr is running, but you must have at least one before you start kralr for the first time


#### Standard Query ####

A standard query will be added as the most recent query terms, but can be bumped out of the way once the KRALR_SLOTS maximum is reached.

#### Initiate a standard query ####

Example:

    ./manage.py kral-query "panda"


#### Permanent Query ####

You could also initiate a permanant query which will always occupy one of the slots in KRALR_SLOTS. It will not get bumped out of the way in favor of standard querys.

#### Initiate a permanent query ####

Example: 

    ./manage.py kral-query --permanent "cheese"


### Starting Celeryd ###

In order for kralr to operate you must also have celery running. The usual ways of starting celery are as follows.

#### Start celery with heartbeat ####

Example:

    ./manage.py celeryd -B --purge

#### Start celery with heartbeat verbose output ####

Example:

    ./manage.py celeryd -B --purge --verbosity=2 --loglevel=INFO

To run celery in production we recommend running it as a daemon.

You can read more about this at: http://celeryproject.org/docs/cookbook/daemonizing.html


### Starting Kral ###

With at least one query defined, and celeryd running, you are ready to start Kral.

#### Start Kral with all enabled plugins ####

Example:

    ./manage.py kral


#### Start kral with all enabled plugins and watch verbose output ####

Example:

    ./manage.py kral --verbose


#### Start kral with only the Facebook plugin ####

Example:

     ./manage.py kral --plugins="Facebook"


#### Start kral with only the Facebook and Twitter plugins with verbose output ####

Example:

     ./manage.py kral --verbose --plugins="Facebook,Twitter" 


### Monitoring Kral ###

If you ever want to take a peek into what Kral is doing and get some basic live stats on the data it is collecting, use kral-monitor

Example:

     ./manage.py kral-monitor


## Notes ##

Many more features coming soon as this project is under active development.

This is by no means production-ready code. Do not actually use it in
production unless you wish to be eaten by a grue.

Questions/Comments? Please check us out on IRC via irc://udderweb.com/#uw
