import argparse
import eventlet
from kral.utils import get_settings
from kral.services import facebook, twitter

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
            print u"{0:7d} | {1:8s} | {2:18s} | {3:140s}".format(count,item['service'], item['user']['name'], item['text'].replace('\n',''))


def stream(queries, services,settings_file=None):
    """
    Yields latest public postings from major social networks for given query or
    queries.

    Keyword arguments:
    queries  -- a single query (string) or multiple queries (list)
    services -- a single service (string) or multiple services (list)

    """
    settings = get_settings(settings_file)

    service_functions = {
        'facebook': facebook,
        'twitter': twitter
    }

    if type(services) is str:
        services = [services]
    if type(queries) is str:
        queries = [queries]

    queue = eventlet.Queue()

    for service in service_functions:
        if service in services:
            eventlet.spawn(service_functions[service], queries, queue, settings)

    while True:
        yield queue.get()
