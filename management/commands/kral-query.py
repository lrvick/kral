import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from kralit.kral.models import Query 
import datetime

class Command(BaseCommand):
    help = 'This command feeds a query to the kralrs for processing'
    
    def handle(self, *args, **options):
        if not args or len(args) > 1:
             return self.stdout.write("Please provide one query.\n")
        q = args[0]
        query, created = Query.objects.get_or_create(text=q)        
            
        if created:
            self.stdout.write("Saved new query: %s\n" % q)
        else:
            if hasattr(settings, 'KRAL_WAIT') and settings.KRAL_WAIT: 
                sec = datetime.timedelta(seconds=settings.KRAL_WAIT)
                if query.last_modified + sec <= datetime.datetime.now():
                    query.last_modified = datetime.datetime.now()
                    query.save() 
                    self.stdout.write("Moved existing query \"%s\" to first in queue for processing.\n" % q)
                else:
                    self.stdout.write("Query \"%s\" must wait at least %s seconds before it can be bumped in priority.\n" % (q,settings.KRAL_WAIT))
                    
            else:
                    query.last_modified = datetime.datetime.now()
                    query.save() 
                    self.stdout.write("Moved existing query \"%s\" to first in queue for processing.\n" % q )
