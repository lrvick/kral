import os
import argparse
from kral import stream
from kral import settings
from ConfigParser import ConfigParser

def csv(value):
    return map(str, value.split(","))

def main():

    parser = argparse.ArgumentParser(description='Tool to interface with kral. Provides the ability to stream one or more keywords from one or more social networks')

    subparsers = parser.add_subparsers(help='sub-command help', dest='parser')

    parser_stream = subparsers.add_parser('stream', help='Stream data from social networks')
    parser_stream.add_argument(
        '--services',
        action='store',
        type=csv,
        default=None,
        help="""Comma seperated list of services you wish to return data from"""
    )
    parser_stream.add_argument(
        '--queries',
        action='store',
        type=csv,
        default=None,
        help="""Comma seperated list of queries to search"""
    )
    parser_stream.add_argument(
        '--config',
        action='store',
        type=str,
        default=None,
        help="""Path to an INI configuration file"""
    )
    parser_stream.add_argument(
        '--count',
        action='store',
        type=int,
        default=None,
        help="""Maximum number of queries to retun"""
    )

    args = parser.parse_args()

    if args.parser == 'stream':
        if not args.config:
            args.config = settings
        else:
            if os.path.exists(args.config):
                config = ConfigParser()
                config.readfp(open(args.config))
                settings['TWITTER_USER'] = config.get('DEFAULT','TWITTER_USER')
                settings['TWITTER_PASS'] = config.get('DEFAULT','TWITTER_PASS')
                settings['FACEBOOK_API_KEY'] = config.get('DEFAULT','FACEBOOK_API_KEY')
                settings['BUZZ_API_KEY'] = config.get('DEFAULT','BUZZ_API_KEY')
                settings['FLICKR_API_KEY'] = config.get('DEFAULT','FLICKR_API_KEY')
            else:
                print "Error: config file '%s' does not exist." % args.config
        count = 0
        for item in stream(args.queries,args.services,settings):
            count +=1
            if args.count and args.count == count:
                break
            print item
