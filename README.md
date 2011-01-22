# Kral #

A social media crawling engine, built on Django. 

Aims to provide a framework for rapidly collect data from social networks
based on defined search criteria. Built to be a foundation for a wide 
range of social applications, to bring accountability to the way in which 
data is collected, and promote others to get involved to help us collect 
as much data as possible with the fewest resources.

## Current Features ##

  * Ability to harvest user information, and posts from Twitter, Facebook, Buzz,
    Identica, Youtube, Flickr... 
  * Ability to expand all short-urls into full real URLs.
  * Modular design. Easily add or disable plugins for different social networks.


## Configuration Options ##


### KRAL_PLUGINS ###

All plugins are enabled by default. To only enable certian plugins, list them in
KRAL_PLUGINS as a list in settings.py

Example:

    KRAL_PLUGINS = ["Twitter", "Facebook"]    


### KRAL_SLOTS ###

Maximum number of query terms to collect data on at the same time

You could for instance, only allow 10 queries to be followed at a time.

Example:

    KRAL_SLOTS = "10"

### KRAL_TIME ###

Minimum amount of time data must be collected for each query.
If all slots are full then this defines how fast slots rotate between queries

Example:

    KRAL_TIME = "5"


With KRAL_TIME set to 5, in the case that all KRAL_SLOTS are full, a new search 
would have to wait 5 seconds before Kral will start checking for any new data. 

The time to set this to will all depend on your amount of traffic and resources.


### KRAL_USERAGENT ###

Use KRAL_USERAGENT to masqurade as another browser

You could esaily use this to set all plugins to masqurade as Firefox, or 
just honestly announche who you are to servers.

Example:

    KRAL_USERAGENT = "KRAL ENGINE IS WATCHING YOU"

NOTE: Pretending to be a real web browser might violate TOS on some services. 
Use at your own risk.


## Starting Kral ##

In order to start collecting data with Kral, you just need to run celery, and 
celery will do the rest. 

The usual ways of starting celery are as follows.

### Start celery with heartbeat ###

Example:

    ./manage.py celeryd -B --purge

### Start celery with heartbeat verbose output ###

Example:

    ./manage.py celeryd -B --purge --verbosity=2 --loglevel=INFO

To run celery in production we recommend running it as a daemon.

You can read more about this at: 

http://celeryproject.org/docs/cookbook/daemonizing.html


## Operating Kral from CLI ##


### Feeding queries to Kral ###

Before running Kral for the first time you must define at least one query term 
for it to collect data on.

You can add new queries at any time, even when kralr is running, but you must 
have at least one before you start kralr for the first time


#### Standard Query ####

A standard query will be added as the most recent query terms, but can be bumped 
out of the way once the KRALR_SLOTS maximum is reached.

#### Initiate a standard query ####

Example:

    ./manage.py kral-query "panda"


#### Permanent Query ####

You could also initiate a permanant query which will bypass KRALR_SLOTS and 
never get bumped out of the way in favor of standard queries. Kralr will always 
devote resourced to collecting data on permanent queries any time it is running.

#### Initiate a permanent query ####

Example: 

    ./manage.py kral-query --permanent "cheese"

### Retreiving data ### 

All data ends up in your choice of channels in your AMQP backend.
This data then can be retreived over the web via Orbited, node.js, APE or any
layer you want to put in front of it that does AMQP <-> HTTP translation.

Results all end up in channels the same name as the query. A query for "android"
will return all its results in the "/android" AMQP channel.

We have had best results with RabbitMQ and Orbited with stomp.js.

You can also connect to those channels with another application designed to
store data which could live locally or on another servier. The FILR project is
being built to do this for Django, but you can use anything that cand read and 
save data from AMQP feeds.

Your mileage may vary.

### Kral Data Format ###

Kral posts are sent out by plugins as single JSON encoded items as follows:

    {
        "service" : "",           # Service Name.
        "user" : {                # User Info 
            "name" : "",          # User Name
            "real_name" : ""      # Real name of user
            "id" : "",            # Unique User ID
            "language": "",       # Spoken language of user
            "utc" : "",           # UTC time offset of user
            "geo" : "",           # Latitude/Logitude User location
            "description" : ""    # User profile description
            "avatar" : "",        # Direct href to avatar image
            "location": "",       # Plain Language User location
            "subscribers": "",    # Number of subscribers
            "subscriptions": "",  # Number of subscriptions
            "postings": "",       # Number of postings made
            "profile": "",        # Href to user profile
            "website": "",        # Href to user website
        }
        "to_users" {               # Attached link(s)
           "0": {                  # Index of link
              "name" : "",         # User Name
              "id" : "",           # Unique User ID
              "service"            # Name of service/Domain hosting link 
              "title" : "",        # Title of item
              "thumbnail" : "",    # Direct href to thumbnail for item
              "href" : "",         # Direct href to item
           },
        },       
        "links" {                 # Attached link(s)
           "0": {                 # Index of link
              "service"            # Name of service/Domain hosting link 
              "title" : "",        # Title of item
              "thumbnail" : "",    # Direct href to thumbnail for item
              "href" : "",         # Direct href to item
           },
        },       
        "id" : "",                # Unique ID
        "geo" : "",               # Latitude/Logitude content creation location
        "application" : "",       # Application used to create this posting
        "location" : "",          # Plain Language content creation location
        "date" : "",              # Date posted
        "source" : "",            # User friendly link to content
        "text" : "",              # Microblog text / Video Title / Etc
        "description" : "",       # Full post text / Decription 
        "keywords" : "",          # Related Keywords
        "category" : "",          # Category of content
        "duration" : "",          # Duration of content (if video)
        "likes" : "",             # Number of users who "liked" this
        "dislikes" : "",          # Number of users who "disliked" this
        "favorites": "",          # Number of users who "favorited" this
        "comments": "",           # Number of users who "commented" this
        "rates": "",              # Number of users who "rated" this
        "rating": "",             # Average "rating" of content
        "min_rating": "",         # Minimum "rating" of content
        "max_rating": "",         # Maximum "rating" of content
    }


## Notes ##

Many more features coming soon as this project is under active development.

This is by no means production-ready code. Do not actually use it in
production unless you wish to be eaten by a grue.

Questions/Comments? Please check us out on IRC via irc://udderweb.com/#uw
