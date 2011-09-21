from setuptools import setup

setup(
    name='kral',
    version='0.1.0',
    author='Tawlk',
    author_email='team@tawlk.com',
    packages=['kral'],
    scripts=['bin/kral'],
    url='http://github.com/Tawlk/kral',
    license='LICENSE',
    description='Library and CLI for performing queries against a wide range of social networks, and returning live streaming results in a normalized format',
    long_description=open('README.md').read(),
    install_requires=[
        'simplejson',
        'eventlet',
        'lxml',
    ]

)
