import unittest
from __init__ import stream
from itertools import islice

class TestStream(unittest.TestCase):

    def setUp(self):
        self.queries = ['android','iphone']

    def test_query_list(self):
        l = list(islice(stream(self.queries),5))
        self.assertEqual(5, len(l), 'Failed to stream with list of queries')

    def test_query_single(self):
        l = list(islice(stream(self.queries[0]),5))
        self.assertEqual(5,len(l))

    def test_service_facebook(self):
        l = list(islice(stream(self.queries[0],'facebook'),5))
        self.assertEqual(5, len(l), 'Failed to stream with single query.')

    def test_service_twitter(self):
        l = list(islice(stream(self.queries[0],'twitter'),5))
        self.assertEqual(5, len(l), 'Failed to stream from Twitter')

    def test_service_identica(self):
        l = list(islice(stream(self.queries[0],'identica'),5))
        self.assertEqual(5, len(l), 'Failed to stream from Identica')

    def test_service_buzz(self):
        l = list(islice(stream(self.queries[0],'buzz'),5))
        self.assertEqual(5, len(l), 'Failed to stream from Buzz')

if __name__ == '__main__':
    unittest.main()
