# Kral #

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

### KRAL_TIME ###

Minimum amount of time data must be collected on a given query before it can be bumped out of line.

Example:

    KRAL_TIME = "5"


With KRAL_TIME set to 5, in the case that all KRAL_SLOTS are full, a new search would have to wait 5 seconds before Kral will start checking for any new data. While waiting a query in line would only retreive any existing data from the database. 

The time to set this to will all depend on your amount of traffic and resources.


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

You could also initiate a permanant query which will bypass KRALR_SLOTS and never get bumped out of the way in favor of standard querys. Kralr will always devote resourced to collecting data on permanent queries any time it is running.

#### Initiate a permanent query ####

Example: 

    ./manage.py kral-query --permanent "cheese"


### Starting Celeryd ###

In order to start collecting data with Kral, you just need to run celery, and celery will do the rest. 

The usual ways of starting celery are as follows.

#### Start celery with heartbeat ####

Example:

    ./manage.py celeryd -B --purge

#### Start celery with heartbeat verbose output ####

Example:

    ./manage.py celeryd -B --purge --verbosity=2 --loglevel=INFO

To run celery in production we recommend running it as a daemon.

You can read more about this at: http://celeryproject.org/docs/cookbook/daemonizing.html


### Monitoring Kral ###

If you ever want to take a peek into what Kral is doing and get some basic live stats on the data it is collecting, use kral-monitor

Example:

     ./manage.py kral-monitor


## Operating Kral from Web API ##

### Setup ###

In order to use the Kral web API you must first include kral.urls in your main urls.py file for your project

Example: 

    urlpatterns = patterns('',
        (r'^kral/.*$', include('kral.urls')),
    )


### Running queries and fetching data ###

For simpilicity and to prevent abuse, this is all built to be transparent on the front end.

In order to fetch data for a particular query for any enabeled social network one only needs to call a url with the name of the plugin, followed by the query, followed by a dot, followed by the format you want the results returned in.

For instance, to return a JSON feed of all the latest tweets related to the term "Android" you would do:

    http://example.com/kral/twitter/Android.json

Or if you wanted to return an RSS feed of all the latest mentions of Facebook mentions of "Rick Astley" you would do:

    http://example.com/kral/facebook/Rick_Astley.rss

All API requests will instantly retreive any matching data from the database, and also request Kral collect new data on this given topic, in respect to the KRAL_TIME and KRAL_SLOTS settings. 


### Kral Data Format ###

Kral posts are created and pushed out by plugins as single JSON encoded items as follows:

    {
        "service" : "",           # Service Name.
        "user" : {                # User Info 
            "name" : "",          #   User Name
            "id" : "",            #   Unique User ID
            "geo" : "",           #   Latitude/Logitude User location
            "avatar" : "",        #   Direct href to avatar image
            "location": "",       #   Plain Language User location
            "subscribers": "",    #   Number of subscribers
            "subscriptions": "",  #   Number of subscriptions
            "profile": "",        #   Href to users profile
        }
        "to_user" : {             # User this post is directed towards.
            "name" : "",          #   User Name 
            "id" : "",            #   Unique User ID
            "geo" : "",           #   Latitude/Logitude User location
            "avatar" : "",        #   Direct href to avatar image
            "location": "",       #   Plain Language User location
            "subscribers": "",    #   Number of subscribers
            "subscriptions": "",  #   Number of subscriptions
            "profile": "",        #   Href to users profile
        }
        "pictures" {              # Attached Pictures
           "0": {                 # Index of picture 
             "thumbnail" : "",    #   Direct href to image thumbnail
             "image" : "",        #   Direct href to picture
           },
        },
        "id" : "",                # Unique ID
        "geo",                    # Latitude/Logitude content creation location
        "location",               # Plain Language content creation location
        "date" : "",              # Date posted
        "source" : "",            # User friendly link to content
        "text" : "",              # Microblog text / Video Title / Etc
        "description" : "",       # Full post text / Decription 
        "keywords" : "",          # Related Keywords
        "category" : "",          # Category of content
        "duration" : "",          # Duration of video
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
