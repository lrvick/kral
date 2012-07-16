import os

#Default config for kral

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
KRAL_PATH = os.path.expanduser('~/.kral')
KRAL_USER_CONFIG_FILE = os.path.join(KRAL_PATH, 'config.py')

if os.path.exists(KRAL_USER_CONFIG_FILE):
    execfile(KRAL_USER_CONFIG_FILE)
