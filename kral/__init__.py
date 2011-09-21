import argparse
from kral import stream
from kral import settings

def csv(value):
    return map(int, value.split(","))

def main():

    parser = argparse.ArgumentParser(cripion='Tool to interface with kral. Provides the ability to stream one or more keywords from one or more social networks')

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
        '--config',
        action='store',
        type=str,
        default=None,
        help="""Path to an INI configuration file"""
    )

    args = parser.parse_args()

    if args.parser == 'stream':
        if not args.settings:
            args.settings = settings
        stream(args.queries,args.services,args.settings)
