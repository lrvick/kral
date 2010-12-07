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
  * Modular design. Easily add or disable "kraling" for different social networks.


## Configuration Options ##


### KRALRS_ENABLED ###

All kralrs are enabled by default. To only enable certian kralrs, list them in KRALRS_ENABLED as a list in settings.py

Example (Only Facebook and Twitter Enabled):

    KRALRS_ENABLED = ["Twitter", "Facebook"]    

### KRALR_SLOTS ###

Maximum number of query terms to collect data on at the same time

Example (Only watch the top ten most recent query terms):

    KRALRS_ENABLED = "10"


### USER_AGENT ###

Use USER_AGENT to masqurade as another browser

Example (Masqurade as Firefox):

    USER_AGENT = "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.7.6) Gecko/20050512 Firefox"


## Operating Kral from CLI##


### Feeding Queries to kral ###

Before running Kral for the first time you must define at least one query term for it to collect data on.

You can add new queries at any time, even when kralr is running, but you must have at least one before you start kralr for the first time


#### Standard Query ####

A standard query will be added as the most recent query terms, but can be bumped out of the way once the KRALR_SLOTS maximum is reached.

Example: Initiate a standard query for pandas

    ./manage.py kral-query "panda"


#### Permanent Query ####

You could also initiate a permanant query which will always occupy one of the slots in KRALR_SLOTS. It will not get bumped out of the way in favor of standard querys.

Example: Initiate a permanent query for cheese

    ./manage.py kral-query --permanent "cheese"


### Starting Celeryd ###

In order for kralr to operate you must also have celery running. The usual ways of starting celery are as follows.

Start celery with heartbeat:

    ./manage.py celeryd -B --purge

Alternatively start celery with verbose output to see the tasks fly by or track down broken stuff:

    ./manage.py celeryd -B --purge --verbosity=2 --loglevel=INFO

To run celery in production we reccomend running it as a daemon.

You can read more about this at: http://celeryproject.org/docs/cookbook/daemonizing.html


### Starting Kral ###

With at least one query defined, and celeryd running, you are ready to start kral

Start all kralrs listed in KRALRS_ENABLED in settings.py (or ALL kralrs if it is not defined):

    ./manage.py kral


Start all kralrs listed in KRALRS_ENABLED in settings.py (or ALL kralrs if it is not defined) and watch verbose output:

    ./manage.py kral --verbose


Start only the Facebook kralr:

     ./manage.py kral --kralrs="Facebook"


Start only the Facebook and Twitter kralrs with verbose output:

     ./manage.py kral --verbose --kralrs="Facebook,Twitter" 


### Monitoring Kral ###

If you ever want to take a peek into what kral is doing and get some basic live stats on the data it is collecting, use kral-monitor

Example:

     ./manage.py kral-monitor


## Notes ##

Many more features coming soon as this project is under active development.

This is by no means production-ready code. Do not actually use it in
production unless you wish to be eaten by a grue.

Questions/Comments? Please check us out on IRC via irc://udderweb.com/#uw
