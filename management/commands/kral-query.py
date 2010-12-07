import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#this command needs follow the docs. This command does not actually do anything yet.

class Command(BaseCommand):
    help = 'This command feeds a query to the kralrs for processing'
    def handle(self, *args, **options):
        print "Sent the query to the kralrs."

