from tasks import ProcessFBStatus

class Facebook(object):
    def __init__(self, query, type="status"):
        self.query = query
        self.type = type
        self.url = "https://graph.facebook.com/search?q=%s&type=post" % self.query 
        self.task = ProcessFBStatus.apply_async(args=[self.url, self.type])

# vim: ai ts=4 sts=4 et sw=4
