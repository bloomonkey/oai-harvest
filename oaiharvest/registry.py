# encoding: utf-8
"""Manage registry of OAI-PMH providers.

usage: oai-reg [-h] [-d DATABASEPATH] {add,rm,list} ...

positional arguments:
  {add,rm,list}         Actions
    add                 Add a new OAI-PMH provider
    rm                  Remove a registered OAI-PMH provider
    list                List registered OAI-PMH provider

optional arguments:
  -h, --help            show this help message and exit
  -d DATABASEPATH, --database DATABASEPATH
                        Path to provider registry database. Currently supports
                        sqlite3 only.

Copyright © 2013, the University of Liverpool <http://www.liv.ac.uk>. All
rights reserved.

Distributed under the terms of the BSD 3-clause License
<http://opensource.org/licenses/BSD-3-Clause>.
"""

import logging
import os
import sqlite3
import sys

from argparse import ArgumentParser
from datetime import datetime

# Import oaipmh for validation purposes
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
from oaipmh.error import XMLSyntaxError
from urllib2 import HTTPError


MAX_NAME_LENGTH = 15


def add_provider(cxn, args):
    """Add a new provider to the registry database.
    
    Process ``args`` to add a new provider to the registry database. Return 0
    for success, 1 for failure (error message should be logged).
    
    ``cxn`` => instance of ``sqlite3.Connection``
    ``args`` => instance of ``argparse.Namespace``
    """
    global logger, MAX_NAME_LENGTH
    addlogger = logger.getChild('add')
    # Validate name
    if len(args.name) > MAX_NAME_LENGTH:
        addlogger.critical('Short name for new provider must be no more than '
                           '{0} characters long'.format(MAX_NAME_LENGTH))
        return 1
    elif args.name.startswith(('http://', 'https://')) or args.name == 'all':
        addlogger.critical('Short name for new provider may not be "all" nor '
                           'may it begin "http://" or "https://"')
        return 1
    # Try to create row now to avoid unnecessary validation if duplicate
    try:
        cxn.execute("INSERT INTO providers(name, lastHarvest) values "
                         "(?, ?)",
                         (args.name, datetime.fromtimestamp(0))
        )
    except sqlite3.IntegrityError:
        addlogger.critical('Unable to add provider "{0}"; '
                           'provider with this name already exists'
                           ''.format(args.name)
                           )
        return 1
    else:
        addlogger.info('Adding provider "{0}"'.format(args.name))
    # Get any missing information
    # Base URL
    if args.url is None:
        args.url = raw_input('Base URL: '.ljust(20))
        if not args.url:
            addlogger.critical('Base URL for new provider not supplied')
            return 1
    # Set up an OAI-PMH client for validating providers
    md_registry = MetadataRegistry()
    md_registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(args.url, md_registry)
    # Validate Base URL by fetching Identify
    try:
        client.identify()
    except (XMLSyntaxError, HTTPError):
        addlogger.critical('Base URL for new provider does not return a valid '
                           'response to an `Identify` request')
        return 1
    # Destination
    if args.dest is None:
        args.dest = raw_input('Destination directory: '.ljust(20))
        if args.dest:
            # Expand user dir
            args.dest = os.path.expanduser(args.dest)
        else:
            addlogger.info('Destination for data for new provider not supplied'
                           ' using default `pwd`: {0}'.format(os.getcwd())
                           )
            args.dest = os.getcwd()
    # metadataPrefix
    # Check that selected metadataPrefix is available from provider
    # Fetch list of available formats
    mdps = dict((mdpinfo[0], mdpinfo[1:])
                    for mdpinfo in
                    client.listMetadataFormats())
    while args.metadataPrefix not in mdps:
        print "Available metadataPrefix values:"
        # List available formats
        for mdp in mdps:
            print mdp, '-', mdps[mdp][1]
        args.metadataPrefix = raw_input('metadataPrefix [oai_dc]:'.ljust(20))
        if not args.metadataPrefix:
            addlogger.info('metadataPrefix for new provider not supplied. '
                           'using default: oai_dc')
            args.metadataPrefix = 'oai_dc'
    cxn.execute("UPDATE providers SET "
                     "url=?, "
                     "destination=?, "
                     "metadataPrefix=? "
                     "WHERE name=?",
                     (args.url,
                      args.dest,
                      args.metadataPrefix,
                      args.name
                      )
    )
    addlogger.info('URL for next harvest: {0}?verb=ListRecords'
                   '&metadataPrefix={1}'
                   '&from={2:%Y-%m-%dT%H:%M:%SZ%z}'
                   ''.format(args.url,
                             args.metadataPrefix,
                             datetime.fromtimestamp(0)
                             )
                   )
    # All done, commit database
    cxn.commit()
    return 0


def rm_provider(cxn, args):
    """Remove existing provider(s) from the registry database.
    
    Process ``args`` to remove provider(s) to the registry database. Return 0
    for success, 1 for failure (error message should be logged).
    
    ``cxn`` => instance of ``sqlite3.Connection``
    ``args`` => instance of ``argparse.Namespace``
    """
    global logger
    rmlogger = logger.getChild('remove')
    for name in args.name:
        with cxn:
            cur = cxn.execute(
                                   "DELETE FROM providers WHERE name=?",
                                   (name,)
                                   )
            if cur.rowcount <= 0:
                rmlogger.error(
                    'No provider named "{0}"; not deleted'.format(name)
                )
            else:
                rmlogger.info('Deleted provider "{0}"'.format(name))
    return 0


def list_providers(cxn, args):
    """List provider(s) currently in the registry database.
    
    Process ``args`` to remove provider(s) to the registry database. Return 0
    for success, 1 for failure (error message should be logged).
    
    ``cxn`` => instance of ``sqlite3.Connection``
    ``args`` => instance of ``argparse.Namespace``
    """
    global logger, MAX_NAME_LENGTH
    listlogger = logger.getChild('remove')
    if args.url:
        sql = 'SELECT name, url FROM providers'
        label = 'Base URL'
    elif args.dest:
        sql = 'SELECT name, destination FROM providers'
        label = "Destination"
    elif args.metadataPrefix:
        sql = 'SELECT name, metadataPrefix FROM providers'
        label = "metadataPrefix"
    elif args.lastHarvest:
        sql = 'SELECT name, lastHarvest FROM providers'
        label = "Last Completed Harvest Time"
    else:
        # Default is smart URL for next harvest request
        sql = ("SELECT name, url || "
               "'?verb=ListRecords&metadataPrefix=' || "
               "metadataPrefix || '&from=' || lastHarvest "
               "FROM providers")
        label = 'URL for next harvest'
    cursor = cxn.execute(sql)
    sys.stdout.write(''.join(['name'.ljust(MAX_NAME_LENGTH + 1),
                              label, '\n']))
    sys.stdout.write(' '.join(['=' * MAX_NAME_LENGTH, '=' * len(label), '\n']))
    for row in cursor:
        sys.stdout.write('{0:<{width}} {1}\n'.format(row[0],
                                                     row[1],
                                                     width=MAX_NAME_LENGTH))
        sys.stdout.flush()


def verify_database(path):
    """Verify that a suitable database exists, create it if not."""
    global logger
    var_logger = logger.getChild('verify')
    try:
        cxn = sqlite3.connect(
            path,
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
        )
    except sqlite3.OperationalError:
        var_logger.critical('Database file "{0}" does not exist and cannot be '
                            'created'.format(path))
        return 1
    # Verify that table exists
    try:
        
        cxn.execute('SELECT name FROM providers')
    except sqlite3.OperationalError:
        # Create the table
        cxn.execute("CREATE TABLE providers("
                    "id integer primary key, "
                    "name varchar({0}) unique, "
                    "url varchar, "
                    "destination varchar, "
                    "metadataPrefix varchar, "
                    "lastHarvest timestamp)".format(MAX_NAME_LENGTH)
                    )
    return cxn


def main(argv=None):
    '''Process command line options, hand off to appropriate function.'''
    global argparser, connection, logger
    if argv is None:
        args = argparser.parse_args()
    else:
        args = argparser.parse_args(argv)
    cxn = verify_database(args.databasePath)
    if not isinstance(cxn, sqlite3.Connection):
        return cxn
    cxn = cxn
    return args.func(cxn, args)


# Set up argument parser
docbits = __doc__.split('\n\n')

argparser = ArgumentParser(description=docbits[0],
                           epilog='\n\n'.join(docbits[-2:]))
argparser.add_argument('-d', '--database',
                       action='store', dest='databasePath',
                       default=os.path.expanduser('~/.oai-harvest/registry.db'),
                       help=("Path to provider registry database. Currently "
                             "supports sqlite3 only.")
                       )
subparsers = argparser.add_subparsers(help='Actions')
# Create the parser for the "add" command
parser_add = subparsers.add_parser('add', help='Add a new OAI-PMH provider')
parser_add.add_argument('name',
                        action='store',
                        help=("Short identifying name for OAI-PMH Provider.")
                        )
parser_add.add_argument('url',
                        action='store',
                        nargs='?',
                        help=("Base URL of OAI-PMH Provider from which to "
                              "harvest.")
                        )
parser_add.add_argument('-p', '--metadataPrefix',
                        action='store', dest='metadataPrefix',
                        default=None,
                        help=("the metadataPrefix of the format (XML Schema) "
                             "in which records should be harvested.")
                        )
group = parser_add.add_mutually_exclusive_group()
group.add_argument('-d', '--dir',
                   action='store', dest='dest',
                   default=None,
                   help=("where to output files for harvested records. "
                         "if not provided, you will be prompted for this "
                         "information")
                   )
parser_add.set_defaults(func=add_provider)
# Create the parser for the "remove" command
parser_rm = subparsers.add_parser('rm',
                                  help='Remove a registered OAI-PMH provider'
                                  )
parser_rm.add_argument('name',
                       action='store',
                       nargs='+',
                       help=("Short identifying name of OAI-PMH Provider "
                             "to remove.")
                       )
parser_rm.set_defaults(func=rm_provider)
# Create the parser for the "list" command
parser_list = subparsers.add_parser('list',
                                    help='List registered OAI-PMH provider'
                                    )
group = parser_list.add_mutually_exclusive_group()
group.add_argument('-u', '--url',
                   action='store_true', dest='url',
                   help="list providers with their base URLs (default)"
                   )
group.add_argument('-d', '--dest',
                   action='store_true', dest='dest',
                   default=False,
                   help="list providers with their destinations"
                   )
group.add_argument('-p', '--metadataPrefix',
                   action='store_true', dest='metadataPrefix',
                   default=False,
                   help="list providers with their metadataPrefixes"
                   )
group.add_argument('-l', '--lastHarvest',
                   action='store_true', dest='lastHarvest',
                   default=False,
                   help=("list providers with the time and date of their "
                         "last completed harvest"
                         )
                   )
parser_list.set_defaults(func=list_providers)

# Check for existence of directory for persistent db, logs etc.
appdir = os.path.expanduser('~/.oai-harvest')
if not os.path.exists(appdir):
    os.mkdir(appdir)

# Set up logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-16s %(levelname)-8s %(message)s',
    datefmt='[%Y-%m-%d %H:%M:%S]',
    filename=os.path.join(appdir, 'registry.log')
)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


if __name__ == "__main__":
    sys.exit(main())
