# encoding: utf-8
"""Harvest records from an OAI-PMH provider.

usage: %prog [-h] [--db DATABASEPATH] [-p METADATAPREFIX]
             [-f YYYY-MM-DD] [-u YYYY-MM-DD] [-s SET] [-d DIR]
             [--delete | --no-delete]
             [-l LIMIT]
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
  -f YYYY-MM-DD, --from YYYY-MM-DD
                        harvest only records added/modified after this date.
  -u YYYY-MM-DD, --until YYYY-MM-DD
                        harvest only records added/modified up to this date.
  -s SET, --set SET     harvest only records within this set
  -d DIR, --dir DIR     where to output files for harvested records.default:
                        current working path
  --delete              respect the server's instructions regarding deletions,
                        i.e. delete the files locally (default)
  --no-delete           ignore the server's instructions regarding deletions,
                        i.e. DO NOT delete the files locally
  -l LIMIT, --limit LIMIT
                        place a limit on the number of records to harvest from
                        each provider

Copyright © 2013, the University of Liverpool <http://www.liv.ac.uk>.
All rights reserved.

Distributed under the terms of the BSD 3-clause License
<http://opensource.org/licenses/BSD-3-Clause>.
"""
from __future__ import with_statement

import logging
import os
import sys

from argparse import ArgumentParser
from datetime import datetime

from oaipmh.client import Client
from oaipmh.error import NoRecordsMatchError

from metadata import DefaultingMetadataRegistry, XMLMetadataReader
from registry import verify_database


class OAIHarvester(object):
    """Abstract Base Class for an OAI-PMH Harvester.
    
    Should be sub-classed in order to do useful things with the harvested
    records (e.g. put them in a directory, VCS repository, local database etc.
    """

    def __init__(self, mdRegistry):
        self._mdRegistry = mdRegistry
    
    def _listRecords(self, baseUrl, metadataPrefix="oai_dc", **kwargs):
        # Generator to yield records from baseUrl in the given metadataPrefix
        # Add metatdataPrefix to args
        kwargs['metadataPrefix'] = metadataPrefix
        client = Client(baseUrl, metadata_registry)
        # Check server timestamp granularity support
        client.updateGranularity()
        for record in client.listRecords(**kwargs):
            yield record

    def harvest(self, baseUrl, metadataPrefix, **kwargs):
        "Harvest records"
        raise NotImplementedError("{0.__class__.__name__} must be sub-classed")


class DirectoryOAIHarvester(OAIHarvester):
    """OAI-PMH Harvester to output harvested records to files in a directory.

    Directory to output files to is specified at object init/construction time.
    """
    
    def __init__(self, mdRegistry, directory,
                 respectDeletions=True, nRecs=0):
        OAIHarvester.__init__(self, mdRegistry)
        self._dir = os.path.abspath(directory)
        self.respectDeletions = respectDeletions
        self.nRecs = nRecs

    def harvest(self, baseUrl, metadataPrefix, **kwargs):
        """Harvest records, return if completed.

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
            fp =  os.path.join(self._dir,
                               "{0}.{1}.xml".format(header.identifier(),
                                                    metadataPrefix)
                               )
            if not os.path.isdir(os.path.dirname(fp)):
                logger.debug("Creating target directory {0}"
                             "".format(self._dir)
                             )
                os.makedirs(os.path.dirname(fp))
            if not header.isDeleted():
                logger.debug('Writing to file {0}'.format(fp))
                with open(fp, 'w') as fh:
                    fh.write(metadata)
                i += 1
            else:
                if self.respectDeletions:
                    logger.debug("Respecting server request to delete file {0}"
                                "".format(fp))
                    try:
                        os.remove(fp)
                    except OSError:
                        # File probably does't exist in destination directory
                        # No further action needed
                        pass
                else:
                    logger.debug("Ignoring server request to delete file {0}"
                                "".format(fp))
        else:
            # Harvesting completed, all available records stored
            return True
        # Loop must have been stopped with ``break``, e.g. due to
        # arbitrary limit
        return False


def main(argv=None):
    """Process command line arguments, harvest records accordingly."""
    global argparser, metadata_registry
    if argv is None:
        args = argparser.parse_args()
    else:
        args = argparser.parse_args(argv)
    logger = logging.getLogger(__name__).getChild('main')
    # Parse from and until into datetime objects
    if args.from_ is not None:
        args.from_ = datetime.strptime(args.from_, "%Y-%m-%d")
    if args.until is not None:
        args.until = datetime.strptime(args.until, "%Y-%m-%d")
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
        if not provider.startswith('http://'):
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
            else:
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
        try:
            completed = harvester.harvest(baseUrl,
                                          args.metadataPrefix,
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
            logger.error(str(e))
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


# Set up argument parser
docbits = __doc__.split('\n\n')

argparser = ArgumentParser(description=docbits[0],
                           epilog='\n\n'.join(docbits[-2:]))
argparser.add_argument('--db', '--database',
                       dest='databasePath',
                       default=os.path.expanduser('~/.oai-harvest/registry.db'),
                       help=("Path to provider registry database. Currently "
                             "supports sqlite3 only.")
                       )
argparser.add_argument('provider',
                       nargs='+',
                       help=("OAI-PMH Provider from which to harvest. This may"
                             " be the base URL of an OAI-PMH server, or the "
                             "short name of a registered provider. You may "
                             "also specify \"all\" for all registered "
                             "providers.")
                       )
argparser.add_argument('-p', '--metadataPrefix',
                       dest='metadataPrefix',
                       help=("the metadataPrefix of the format (XML Schema) "
                             "in which records should be harvested.")
                       )
argparser.add_argument("-f", "--from",
                       dest="from_",
                       metavar="YYYY-MM-DD",
                       help=("harvest only records added/modified after this "
                             "date.")
                       )
argparser.add_argument("-u", "--until",
                       dest="until",
                       metavar="YYYY-MM-DD",
                       help=("harvest only records added/modified up to this "
                             "date.")
                       )
argparser.add_argument("-s", "--set",
                       dest="set",
                       help=("harvest only records within this set")
                       )

group = argparser.add_mutually_exclusive_group()
group.add_argument('-d', '--dir',
                   dest='dir',
                   help=("where to output files for harvested records."
                         "default: current working path")
                   )
# What to do about deletions
group = argparser.add_mutually_exclusive_group()
group.set_defaults(deletions=True)
group.add_argument("--delete",
                   action='store_true',
                   dest='deletions',
                   help=("respect the server's instructions regarding "
                         "deletions, i.e. delete the files locally (default)")
                   )
group.add_argument("--no-delete",
                   action='store_false',
                   dest='deletions',
                   help=("ignore the server's instructions regarding "
                         "deletions, i.e. DO NOT delete the files locally")
                   )
argparser.add_argument("-l", "--limit",
                       dest="limit",
                       type=int,
                       help=("place a limit on the number of records to "
                             "harvest from each provider")
                       )

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
    format='%(asctime)s %(name)-16s %(levelname)-8s %(message)s',
    datefmt='[%Y-%m-%d %H:%M:%S]',
    filename=os.path.join(appdir, 'harvest.log')
)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
ch.setFormatter(formatter)
logging.getLogger(__name__).addHandler(ch)


if __name__ == "__main__":
    sys.exit(main())
