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

  * Python 2.6 - 2.7
  * pip

## Usage / Installation ##

1. Install kral

    ```bash
    pip install -e git+https://github.com/Tawlk/kral/#egg=kral
    ```

2. Configure

    Edit ~/kral/config.ini file as follows:

    ```ini
    [ DEFAULT ]
    TWITTER_USER = your_user
    TWITTER_PASS = your_pass
    BUZZ_API_KEY = your_key
    FACEBOOK_API_KEY = your_key
    FLICKR_API_KEY = your_key
    ```

3.  Collect data

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

    You can also collect data via the CLI interface.

    ```bash
    kral stream  --services="twitter,facebook" --queries="android"
    ```

    For more information on the CLI interface run:

    ```bash
    kral --help
    ```

## Notes ##

Many more features coming soon as this project is under active development.

This is by no means production-ready code. Do not actually use it in
production unless you wish to be eaten by a grue.

Questions/Comments? Please check us out on IRC via irc://udderweb.com/#uw
