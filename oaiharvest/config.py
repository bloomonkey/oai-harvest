# encoding: utf-8
"""Configure harvesting of records from OAI-PMH provider(s).

"""

import logging
import os
import sqlite3
import sys

from argparse import ArgumentParser
from datetime import datetime


class InputError(ValueError):
    """Custom Exception class for user input errors."""
    pass


def add_provider(args):
    global logger
    addlogger = logger.getChild('add')
    # Get any missing information
    if args.url is None:
        args.url = raw_input('Base URL:'.ljust(20))
        if not args.url:
            addlogger.critical('Base URL for new provider not supplied')
            return 1
    if args.dest is None:
        args.dest = raw_input('destination directory: '.ljust(20))
        if not args.dest:
            addlogger.info('Destination for data for new provider not supplied'
                           ' using default `pwd`: {0}'.format(os.getcwd())
                           )
            args.dest = os.getcwd()
    if args.metadataPrefix is None:
        args.metadataPrefix = raw_input('metadataPrefix [oai_dc]:'.ljust(20))
        if not args.metadataPrefix:
            addlogger.info('metadataPrefix for new provider not supplied. '
                           'using default: oai_dc')
            args.metadataPrefix = 'oai_dc'
    try:
        with args.cxn:
            args.cxn.execute("INSERT INTO providers(name, url, destination, "
                             "metadataPrefix, lastHarvest) values "
                             "(?, ?, ?, ?, ?)",
                             (args.name,
                              args.url,
                              args.dest,
                              args.metadataPrefix,
                              datetime.fromtimestamp(0)
                              )
            )
    except sqlite3.IntegrityError:
        addlogger.critical('Unable to add provider "{0}"; '
                           'provider with this name already exists'
                           ''.format(args.name)
                           )
        return 1
    else:
        addlogger.info('Added provider "{0}": {1}'.format(args.name,
                                                          args.url))
        return 0

def rm_provider(args):
    global logger
    rmlogger = logger.getChild('remove')
    for name in args.name:
        with args.cxn:
            cur = args.cxn.execute(
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


def verify_database(path):
    """Verify that a suitable database exists, create it if not."""
    logger = logging.getLogger(__name__).getChild('verify')
    try:
        cxn = sqlite3.connect(
            path,
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
        )
    except sqlite3.OperationalError:
        logger.critical('Database file "{0}" does not exist'.format(path))
        return 1
    # Verify that table exists
    try:
        
        cxn.execute('SELECT name FROM providers')
    except sqlite3.OperationalError:
        # Create the table
        cxn.execute("CREATE TABLE providers("
                    "id integer primary key, "
                    "name varchar unique, "
                    "url varchar, "
                    "destination varchar, "
                    "metadataPrefix varchar, "
                    "lastHarvest timestamp)"
                    )
    return cxn


def main(argv=None):
    '''Command line options.'''
    global argparser, connection, logger
    if argv is None:
        args = argparser.parse_args()
    else:
        args = argparser.parse_args(argv)
    cxn = verify_database(args.databasePath)
    if not isinstance(cxn, sqlite3.Connection):
        return cxn
    args.cxn = cxn
    return args.func(args)


# Set up argument parser
docbits = __doc__.split('\n\n')

argparser = ArgumentParser(description=docbits[0],
                           epilog='\n\n'.join(docbits[-2:]))
argparser.add_argument('-d', '--database',
                       action='store', dest='databasePath',
                       default=os.path.expanduser('~/.oai-harvest/config.db'),
                       help=("Path to database used for making configurations "
                             "persistent.")
                       )
subparsers = argparser.add_subparsers(help='Actions')
# Create the parser for the "add" command
parser_add = subparsers.add_parser('add', help='Add a new OAI-PMH target')
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
                                  help='Remove a registered OAI-PMH target'
                                  )
parser_rm.add_argument('name',
                       action='store',
                       nargs='+',
                       help=("Short identifying name of OAI-PMH Provider "
                             "to remove.")
                       )
parser_rm.set_defaults(func=rm_provider)


appdir = os.path.expanduser('~/.oai-harvest')
if not os.path.exists(appdir):
    os.mkdir(appdir)

# Set up logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-16s %(levelname)-8s %(message)s',
    datefmt='[%Y-%m-%d %H:%M:%S]',
    filename=os.path.join(appdir, 'config.log')
)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


if __name__ == "__main__":
    sys.exit(main())
