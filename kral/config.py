#Config for Kral.

#Default settings that apply to all services.
TIME_FORMAT = ""
LANG = "en"
USER_AGENT = ""

#Each service is a key-value mapping
TWITTER = {
    'user': '',
    'password': '',
}

FACEBOOK = {
    'app_id' : '',
    'app_secret' : '',
}

YOUTUBE = {
    'orderby': 'published',
    'maxresults': 25,
    'mode': 'most_recent',
    'time': 'today',
}
REDDIT = {
    'orderby': 'relevance',
}
