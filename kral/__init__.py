# -*- coding: utf-8 -*-
import argparse
import eventlet
from kral.services import facebook, twitter, youtube, reddit
import time
import os
import shutil
from kral import config

def csv(value):
    return map(str, value.split(","))

def main():

    if not os.path.exists(config.KRAL_PATH):
        os.makedirs(config.KRAL_PATH)

        #copy initial config for first time
        if not os.path.exists(config.KRAL_USER_CONFIG_FILE):
            config_file = os.path.join(config.PROJECT_PATH, 'user_config.py')
            target_config = config.KRAL_USER_CONFIG_FILE
            shutil.copy(config_file, target_config)

            print("First time run created a config in ~/.kral that Kral will use. Please make sure to set the proper options according to the documentation and then re-run your previous command.")
            return

    parser = argparse.ArgumentParser(description='Tool to interface with kral. Provides the ability to stream one or more keywords from one or more social networks')

    subparsers = parser.add_subparsers(help='sub-command help', dest='parser')

    parser_stream = subparsers.add_parser('stream', help='Stream data from social networks')
    parser_stream.add_argument(
        '--services',
        action='store',
        type=csv,
        default="twitter",
        help="""Comma seperated list of services you wish to return data from"""
    )
    parser_stream.add_argument(
        '--queries',
        action='store',
        type=csv,
        default="android",
        help="""Comma seperated list of queries to search"""
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

        for item in stream(args.queries, args.services):
            count +=1
            if args.count and args.count == count:
                break
            try:
                # so some strings seem to break even unicode-escape... so we just dont display those.
                # Temp hack until we can find a sane way to deal with this unicode inconsistancy.
                print u"{0:7d} | {1:8s} | {2:8s} | {3:22s} | {4:5d} | {5:140s}".format(count,item['service'], item['query'], item['user']['name'], item['user']['subscribers'], item['text'].replace('\n','').encode('unicode-escape'))
            except:
                pass

def stream(query_list, service_list=[]):
    """
    Yields latest public postings from major social networks for given query or
    queries.

    Arguments:
    query_list (str/list)  -- a single query (string) or multiple queries (list)

    Keyword arguments:
    service_list (str/list) -- a single service (string) or multiple services (list) by 
                        default all will be used
    """
    kral_start_time = int(time.time())

    service_functions = {
        'facebook': facebook.stream,
        'twitter': twitter.stream,
        'youtube': youtube.stream,
        #'plus' : plus.stream,
        'reddit': reddit.stream,
    }

    if type(service_list) is str:
        service_list = [service_list]
    if type(query_list) is str:
        query_list = [query_list]

    queue = eventlet.Queue()

    for service in service_functions:
        if not service_list:
            eventlet.spawn(service_functions[service], query_list, queue, kral_start_time)
        elif service in service_list:
            eventlet.spawn(service_functions[service], query_list, queue, kral_start_time)

    while True:
        yield queue.get()

if __name__ == '__main__':
    print("Starting stream ... ")
    for i in stream(['android', 'iphone', 'bieber',], ['twitter',]):
        print i
