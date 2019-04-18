# encoding: utf-8
"""Harvest records from an OAI-PMH provider.

usage: %prog [-h] [--db DATABASEPATH] [-p METADATAPREFIX] [-r TOKEN]
             [-f YYYY-MM-DD] [-u YYYY-MM-DD] [-s SET] [-b HH:MM HH:MM]
             [-d DIR] [--delete | --no-delete] [-l LIMIT]
             [--create-subdirs | --subdirs-on SUBDIRS]
             provider [provider ...]

positional arguments:
  provider              OAI-PMH Provider from which to harvest. This may be
                        the base URL of an OAI-PMH server, or the short name
                        of a registered provider. You may also specify "all"
                        for all registered providers.

optional arguments:
  -h, --help            show this help message and exit
  --db DATABASEPATH, --database DATABASEPATH
                        Path to provider registry database. Currently supports
                        sqlite3 only.
  -p METADATAPREFIX, --metadataPrefix METADATAPREFIX
                        the metadataPrefix of the format (XML Schema) in which
                        records should be harvested.
  -r TOKEN, --resume-from TOKEN
                        start at the given resumption TOKEN
  -f YYYY-MM-DD, --from YYYY-MM-DD
                        harvest only records added/modified after this date.
  -u YYYY-MM-DD, --until YYYY-MM-DD
                        harvest only records added/modified up to this date.
  -s SET, --set SET     harvest only records within this set
  -b HH:MM HH:MM, --between HH:MM HH:MM
                        harvest only between the first and the second wall
                        clock time (enables incremental harvesting)
  -d DIR, --dir DIR     where to output files for harvested records.default:
                        current working path
  --delete              respect the server's instructions regarding deletions,
                        i.e. delete the files locally (default)
  --no-delete           ignore the server's instructions regarding deletions,
                        i.e. DO NOT delete the files locally
  -l LIMIT, --limit LIMIT
                        limit the number of records to harvest from each
                        provider
  --create-subdirs      create target subdirs (based on / characters in
                        identifiers) ifthey don't exist. To use something
                        other than /, use the newer--subdirs-on option
  --subdirs-on SUBDIRS  create target subdirs based on occurrences of the
                        given characterin identifiers

Copyright (c) 2013, the University of Liverpool <http://www.liv.ac.uk>.
All rights reserved.

Distributed under the terms of the BSD 3-clause License
<http://opensource.org/licenses/BSD-3-Clause>.
"""
from __future__ import with_statement, absolute_import

import ast
import codecs
import logging
import os
import platform
import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta
from time import sleep

import six.moves.urllib.parse as urllib
from .client import Client
from oaipmh.error import NoRecordsMatchError
from six import string_types

from .exceptions import NotOAIPMHBaseURLException
from .metadata import DefaultingMetadataRegistry, XMLMetadataReader
from .registry import verify_database


class OAIHarvester(object):
    """Abstract Base Class for an OAI-PMH Harvester.

    Should be sub-classed in order to do useful things with the harvested
    records (e.g. put them in a directory, VCS repository, local database etc.
    """

    def __init__(self, mdRegistry):
        self._mdRegistry = mdRegistry

    def pause(self, now, until):
        """ Unconditionally pause the process from `now` to `until`. """
        logger = logging.getLogger(__name__).getChild('OAIHarvester.pause')
        logger.info('Pausing until {} (incremental harvest).'.format(until))
        sleep((until - now) / timedelta(seconds=1))

    def maybe_pause_if_incremental(self, time_range):
        """ Pause the process depending on incremental time range settings. """
        if time_range is None:
            return
        now = datetime.now()
        start = datetime.combine(now.date(), time_range[0].time())
        stop = datetime.combine(now.date(), time_range[1].time())
        if now < start:
            if now < stop < start:
                return
            return self.pause(now, start)
        if start < stop <= now:
            return self.pause(now, start + timedelta(days=1))
        # If we reach this point, there is no need to pause.

    def _listRecords(self, baseUrl, metadataPrefix="oai_dc", **kwargs):
        # Generator to yield records from baseUrl in the given metadataPrefix
        # Add metatdataPrefix to args
        kwargs['metadataPrefix'] = metadataPrefix
        client = Client(baseUrl, self._mdRegistry, recover=kwargs.pop('recover', False))
        incremental_range = kwargs.pop('between', None)
        # Check that baseUrl actually represents an OAI-PMH target
        try:
            client.identify()
        except IndexError:
            raise NotOAIPMHBaseURLException(
                "{0} does not appear to be an OAI-PMH compatible base URL"
                "".format(baseUrl)
            )
        # Check server timestamp granularity support
        client.updateGranularity()
        self.maybe_pause_if_incremental(incremental_range)
        for record in client.listRecords(**kwargs):
            # Unit test hotfix
            header, metadata, about = record
            # Fix pyoai returning a "b'...'" string for py3k
            if isinstance(metadata, str) and metadata.startswith("b'"):
                metadata = ast.literal_eval(metadata).decode("utf-8")
            yield (header, metadata, about)
            if client.XMLParser.error_log :
                logging.getLogger(__name__).getChild('XMLParser').warning(
                'Recoverable XMLParser error on: %s', header.identifier() )
            self.maybe_pause_if_incremental(incremental_range)

    def harvest(self, baseUrl, metadataPrefix, **kwargs):
        "Harvest records"
        raise NotImplementedError(
            "{0.__class__.__name__} must be sub-classed".format(self)
        )


class DirectoryOAIHarvester(OAIHarvester):
    """OAI-PMH Harvester to output harvested records to files in a directory.

    Directory to output files to is specified at object init/construction
    time.
    """

    def __init__(self, mdRegistry, directory,
                 respectDeletions=True, createSubDirs=False, nRecs=0):
        OAIHarvester.__init__(self, mdRegistry)
        self._dir = os.path.abspath(directory)
        self.respectDeletions = respectDeletions
        self.createSubDirs = createSubDirs
        self.nRecs = nRecs

    def harvest(self, baseUrl, metadataPrefix, **kwargs):
        """Harvest records, return if completed.

        :rtype: bool
        :returns: Were all available records fetched and stored?

        Harvest records, output records to files in the directory and
        return a boolean for whether or not all of the records that the
        server could return were actually stored locally.
        """
        logger = logging.getLogger(__name__).getChild(self.__class__.__name__)
        # A counter for the number of records actually returned
        # enumerate() not used as it would include deleted records
        i = 0
        for header, metadata, about in self._listRecords(
                 baseUrl,
                 metadataPrefix=metadataPrefix,
                 **kwargs):
            if self.nRecs and self.nRecs > 0 and self.nRecs <= i:
                logger.info("Stopping harvest; set limit of {0} has been "
                            "reached".format(self.nRecs))
                break

            fp = self._get_output_filepath(header, metadataPrefix)
            self._ensure_dir_exists(fp)

            if not header.isDeleted():
                logger.debug('Writing to file {0}'.format(fp))
                with codecs.open(fp, "w", encoding="utf-8") as fh:
                    fh.write(metadata)
                i += 1
            else:
                if self.respectDeletions:
                    logger.debug("Respecting server request to delete file "
                                 "{0}".format(fp))
                    try:
                        os.remove(fp)
                    except OSError:
                        # File probably does't exist in destination directory
                        # No further action needed
                        pass
                else:
                    logger.debug("Ignoring server request to delete file "
                                 "{0}".format(fp))
        else:
            # Harvesting completed, all available records stored
            return True
        # Loop must have been stopped with ``break``, e.g. due to
        # arbitrary limit
        return False

    def _ensure_dir_exists(self, fp):
        logger = logging.getLogger(__name__).getChild(self.__class__.__name__)
        if not os.path.isdir(os.path.dirname(fp)):
            # Missing base directory or sub-directory
            logger.debug("Creating target directory {0}".format(self._dir))
            os.makedirs(os.path.dirname(fp))

    def _get_output_filepath(self, header, metadataPrefix):
        filename = "{0}.{1}.xml".format(
            header.identifier(),
            metadataPrefix)

        protected = []
        if platform.system() != 'Windows':
            protected.append(':')

        if self.createSubDirs:
            if isinstance(self.createSubDirs, string_types):
                # Replace specified character with platform path separator
                filename = filename.replace(self.createSubDirs, os.path.sep)

            # Do not escape path separators, so that sub-directories
            # can be created
            protected.append(os.path.sep)

        filename = urllib.quote(filename, ''.join(protected))
        fp = os.path.join(self._dir, filename)
        return fp


def main(argv=None):
    """Process command line arguments, harvest records accordingly."""
    global argparser, metadata_registry
    if argv is None:
        args = argparser.parse_args()
    else:
        args = argparser.parse_args(argv)
    logger = logging.getLogger(__name__).getChild('main')
    # Establish connection to persistent storage
    cxn = verify_database(args.databasePath)
    # Make a set of providers - don't repeat for repeated arguments
    providers = set(args.provider)
    # Check for "all" providers
    if "all" in args.provider:
        # Remove "all" from set
        providers.remove('all')
        # Update set with all registered providers
        providers.update([row[0]
                          for row
                          in cxn.execute('SELECT name FROM providers')
                          ])
    for provider in providers:
        if not provider.startswith(('http://', 'https://')):
            # Fetch details from provider registry
            cursor = cxn.execute('SELECT url, '
                                 'destination, '
                                 'metadataPrefix, '
                                 'lastHarvest [timestamp]'
                                 'FROM providers '
                                 'WHERE name=?', (provider,))
            row = cursor.fetchone()
            if row is None:
                logger.error("Provider {0} does not exists in database {1}"
                             "".format(provider, args.databasePath))
                continue
            baseUrl = row[0]
            logger.info('Harvesting from registered provider {0} - {1}'
                        ''.format(provider, baseUrl))
            # Allow over-ride of default destination
            if args.dir is not None:
                logger.warning('Value for command line option --dir'
                               ' over-rides registered destination')
            else:
                args.dir = row[1]
            # Allow over-ride of default metadataPrefix
            if args.metadataPrefix is not None:
                logger.warning('Value for command line option --metadataPrefix'
                               ' over-rides registered value')
            else:
                args.metadataPrefix = row[2]
            # Allow over-ride of stored lastHarvest time
            # e.g. to repair some locally munged data
            if args.from_ is not None:
                logger.warning('Value for command line option --from'
                               ' over-rides recorded lastHarvest timestamp')
            elif args.resumptionToken is None:
                args.from_ = row[3]
        else:
            baseUrl = provider
            logger.info('Harvesting from {0}'.format(baseUrl))
            if args.dir is None:
                args.dir = '.'

        if args.metadataPrefix is None:
            args.metadataPrefix = 'oai_dc'

        # Init harvester object
        harvester = DirectoryOAIHarvester(metadata_registry,
                                          os.path.abspath(args.dir),
                                          respectDeletions=args.deletions,
                                          createSubDirs=args.subdirs,
                                          nRecs=args.limit
                                          )
        # Create a dictionary of keyword args
        # Avoid sending kwargs with value of None - e.g. set=None causes
        # error on servers that don't support set hierarchy.
        kwargs = {}
        if args.from_ is not None:
            kwargs['from_'] = args.from_
        if args.until is not None:
            kwargs['until'] = args.until
            # Set the end time of the harvest slice with which to
            # update the registry if necessary
            lastHarvestEndTime = args.until
        else:
            # Set the end time of the harvest slice to now
            # The first request might create a snapshot of the data on
            # the provider server in order for resumption tokens to work
            # correctly. Any records added after this snapshot, but
            # before completion of harvesting must be included in next
            # harvest.
            lastHarvestEndTime = datetime.now()

        if args.set is not None:
            kwargs['set'] = args.set
        if args.between is not None:
            kwargs['between'] = args.between
        if args.resumptionToken is not None:
            kwargs['resumptionToken'] = args.resumptionToken
        try:
            completed = harvester.harvest(baseUrl,
                                          args.metadataPrefix,
                                          recover=True,
                                          **kwargs
                                          )
        except NoRecordsMatchError:
            # Nothing to harvest
            completed = True
            logger.info("0 records to harvest")
            logger.debug("The combination of the values of the from={0}, "
                         "until={1}, set=(N/A) and metadataPrefix={2} "
                         "arguments results in an empty list."
                         "".format(args.from_,
                                   args.until,
                                   args.metadataPrefix)
                         )
        except Exception as e:
            # Log error
            logger.error(str(e), exc_info=True)
            # Continue to next provide without updating database lastHarvest
            continue

        if completed:
            # Update lastHarvest time for registered provider
            with cxn:
                cxn.execute("UPDATE providers SET lastHarvest=? WHERE name=?",
                            (lastHarvestEndTime, provider)
                            )
        else:
            logger.warn("Harvesting incomplete; additional records were "
                        "available from the server")


def parse_date(argument):
    """ Date parser to be used as type argument for argparser options. """
    return datetime.strptime(argument, "%Y-%m-%d")


def parse_time(argument):
    """ Time parser to be used as type argument for argparser options. """
    return datetime.strptime(argument, "%H:%M")


# Set up argument parser
docbits = __doc__.split('\n\n')

argparser = ArgumentParser(
    description=docbits[0],
    epilog='\n\n'.join(docbits[-2:]))
argparser.add_argument(
    '--db',
    '--database',
    dest='databasePath',
    default=os.path.expanduser('~/.oai-harvest/registry.db'),
    help=("Path to provider registry database. Currently "
          "supports sqlite3 only."))
argparser.add_argument(
    'provider',
    nargs='+',
    help=("OAI-PMH Provider from which to harvest. This may"
          " be the base URL of an OAI-PMH server, or the "
          "short name of a registered provider. You may "
          "also specify \"all\" for all registered "
          "providers."))
argparser.add_argument(
    '-p',
    '--metadataPrefix',
    dest='metadataPrefix',
    help=("the metadataPrefix of the format (XML Schema) "
          "in which records should be harvested."))
argparser.add_argument(
    '-r',
    '--resume-from',
    dest='resumptionToken',
    metavar='TOKEN',
    help='start at the given resumption TOKEN',
)
argparser.add_argument(
    "-f",
    "--from",
    type=parse_date,
    dest="from_",
    metavar="YYYY-MM-DD",
    help=("harvest only records added/modified after this "
          "date."))
argparser.add_argument(
    "-u",
    "--until",
    type=parse_date,
    dest="until",
    metavar="YYYY-MM-DD",
    help=("harvest only records added/modified up to this "
         "date."))
argparser.add_argument(
    "-s",
    "--set",
    dest="set",
    help=("harvest only records within this set"))
argparser.add_argument(
    '-b',
    '--between',
    type=parse_time,
    nargs=2,
    metavar='HH:MM',
    help=('harvest only between the first and the second wall clock time '
        '(enables incremental harvesting)'),
)

group = argparser.add_mutually_exclusive_group()
group.add_argument(
    '-d',
    '--dir',
    dest='dir',
    help=("where to output files for harvested records."
          "default: current working path"))
# What to do about deletions
group = argparser.add_mutually_exclusive_group()
group.set_defaults(deletions=True)
group.add_argument(
    "--delete",
    action='store_true',
    dest='deletions',
    help=("respect the server's instructions regarding "
          "deletions, i.e. delete the files locally (default)"))
group.add_argument(
    "--no-delete",
    action='store_false',
    dest='deletions',
    help=("ignore the server's instructions regarding "
          "deletions, i.e. DO NOT delete the files locally"))
argparser.add_argument(
    "-l",
    "--limit",
    dest="limit",
    type=int,
    help="limit the number of records to harvest from each provider")
# What to do about sub-directories
group = argparser.add_mutually_exclusive_group()
group.set_defaults(subdirs=None)
group.add_argument(
    "--create-subdirs",
    action='store_true',
    dest='subdirs',
    help=("create target subdirs (based on / characters in identifiers) if"
          "they don't exist. To use something other than /, use the newer"
          "--subdirs-on option")
                   )
group.add_argument(
    "--subdirs-on",
    action='store',
    dest='subdirs',
    help=("create target subdirs based on occurrences of the given character"
          "in identifiers"))


# Set up metadata registry
xmlReader = XMLMetadataReader()
metadata_registry = DefaultingMetadataRegistry(defaultReader=xmlReader)

# Check for existence of directory for persistent db, logs etc.
appdir = os.path.expanduser('~/.oai-harvest')
if not os.path.exists(appdir):
    os.mkdir(appdir)

# Set up logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)-8s %(message)s',
    # format='%(asctime)s %(name)-16s %(levelname)-8s %(message)s',
    # datefmt='[%Y-%m-%d %H:%M:%S]',
    # filename=os.path.join(appdir, 'harvest.log')
    )

#ch = logging.StreamHandler()
ch = logging.FileHandler( os.path.join( appdir, 'harvest.log'))
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s %(name)-16s %(levelname)-8s %(message)s',
    '[%Y-%m-%d %H:%M:%S]')
#formatter = logging.Formatter('%(levelname)-8s %(message)s')
ch.setFormatter(formatter)
logging.getLogger(__name__).addHandler(ch)

from lxml import etree

class XMLErrorLog( etree.PyErrorLog ):
    new_map = { 1: 30, 2: 30, 3: 30 }
    def __init__( self, *args, **kwargs ):
        etree.PyErrorLog.__init__( self, *args, **kwargs )
        self.level_map.update( self.new_map )
    def receive(self, log_entry ):
        logrepr = "%s:%d:%d:%s%s.%s:[%s]" % (
            log_entry.filename, log_entry.line, log_entry.column, "",
            log_entry.domain_name, log_entry.type_name, log_entry.message)
        self.log( log_entry, logrepr )

etree.use_global_python_log(XMLErrorLog(logger=logging.getLogger(__name__).getChild('XMLParser')))


if __name__ == "__main__":
    sys.exit(main())
