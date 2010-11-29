import time,feedparser,re  #search - what is this?
from datetime import datetime
from django.utils.encoding import smart_unicode
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

def route_listener(request)
	get = request.GET
	return HttpResponse(get)



# vim: ai ts=4 sts=4 et sw=4
