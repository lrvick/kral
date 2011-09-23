import argparse
import eventlet
from kral.utils import get_settings
from kral.services import facebook, twitter

def csv(value):
    return map(str, value.split(","))

def main():

    parser = argparse.ArgumentParser(description='Tool to interface with kral. Provides the ability to stream one or more keywords from one or more social networks')

    subparsers = parser.add_subparsers(help='sub-command help', dest='parser')

    parser_setup = subparsers.add_parser(
        'setup',
        help="Set up authentication data for all social network API kral needs to access",
    )
    parser_setup.add_argument(
        '--services',
        action='store',
        type=csv,
        default=None,
        help="""Comma seperated list of services you wish to set up for streaming"""
    )

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
            print u"{0:7d} | {1:8s} | {2:18s} | {3:140s}".format(count,item['service'], item['user']['name'], item['text'].replace('\n',''))


    if args.parser == 'setup':
        print "Running setup for all services"
        facebook.setup()
        twitter.setup()

def stream(query_list, service_list, settings_file=None):
    """
    Yields latest public postings from major social networks for given query or
    queries.

    Keyword arguments:
    query_list   -- a single query (string) or multiple queries (list)
    service_list -- a single service (string) or multiple services (list)

    """
    settings = get_settings(settings_file)

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
            eventlet.spawn(service_functions[service], query_list, queue, settings)

    while True:
        yield queue.get()
