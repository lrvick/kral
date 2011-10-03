import argparse
import eventlet
from kral.services import facebook, twitter
from utils import config_init
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
        count = 0
        for item in stream(args.queries,args.services,args.config):
            count +=1
            if args.count and args.count == count:
                break
            print u"{0:7d} | {1:8s} | {2:22s} | {3:5d} | {4:140s}".format(count,item['service'], item['user']['name'], item['user']['subscribers'], item['text'].replace('\n',''))


def stream(query_list, service_list, config_file=None):
    """
    Yields latest public postings from major social networks for given query or
    queries.

    Keyword arguments:
    query_list   -- a single query (string) or multiple queries (list)
    service_list -- a single service (string) or multiple services (list)

    """
    config_file = config_init(config_file)

    config = ConfigParser()
    config.readfp(config_file)

    service_functions = {
        'facebook': facebook.stream,
        'twitter': twitter.stream
    }

    if type(service_list) is str:
        service_list = [service_list]
    if type(query_list) is str:
        query_list = [query_list]

    queue = eventlet.Queue()

    for service in service_functions:
        if service in service_list:
            eventlet.spawn(service_functions[service], query_list, queue, config)

    while True:
        yield queue.get()
