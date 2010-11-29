import djcelery,os

djcelery.setup_loader()

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'postgresql_psycopg2', 
        'NAME': 'your_db_name',                      
        'USER': 'your_db_user',                     
        'PASSWORD': 'your_pass',          
    }
}

TIME_ZONE = 'America/New_York'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = os.path.join(PROJECT_PATH,'media')

MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/media/admin/'

SECRET_KEY = 'type_a_bunch_of_random_characters_here'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
		os.path.join(PROJECT_PATH,'templates'),
)

INSTALLED_APPS = (
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.sites',
#    'django.contrib.messages',
#    'django.contrib.comments',
#    'django.contrib.admin',
    'south',
    'djcelery',
    'kral',
)

#User agent to fake when scraping data
USER_AGENT="Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.7.6) Gecko/20050512 Firefox"

#AMPQ Server Info
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672
BROKER_VHOST = "/"
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"

#Load installation specific settings/passwords from external file with restrictive permissions
execfile(os.path.join(PROJECT_PATH,'.private-settings'))

# vim: ai ts=4 sts=4 et sw=4
