# encoding: utf-8
"""Harvest records from an OAI-PMH provider.

positional arguments:
  provider              OAI-PMH Provider from which to harvest.

optional arguments:
  -h, --help            show this help message and exit
  -p METADATAPREFIX, --metadataPrefix METADATAPREFIX
                        where to output files for harvested records. default
                        is current working path
  -f YYYY-MM-DD, --from YYYY-MM-DD
                        harvest only records added/modified after this date.
  -u YYYY-MM-DD, --until YYYY-MM-DD
                        harvest only records added/modified up to this date.
  -d DIR, --dir DIR     where to output files for harvested records.default:
                        current working path

Copyright © 2013, the University of Liverpool <http://www.liv.ac.uk>.
All rights reserved.

Distributed under the terms of the BSD 3-clause License
<http://opensource.org/licenses/BSD-3-Clause>.
"""

import logging
import os
import sys

from argparse import ArgumentParser
from datetime import datetime

from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

from metadata import DefaultingMetadataRegistry, XMLMetadataReader


class OAIHarvester(object):

    def __init__(self, mdRegistry):
        self._mdRegistry = mdRegistry
    
    def _listRecords(self, baseUrl, metadataPrefix="oai_dc", **kwargs):
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
    
    def __init__(self, mdRegistry, directory):
        OAIHarvester.__init__(self, mdRegistry)
        self._dir = directory

    def harvest(self, baseUrl, metadataPrefix, **kwargs):
        logger = logging.getLogger(__name__).getChild(self.__class__.__name__)
        for header, metadata, about in self._listRecords(
                 baseUrl,
                 metadataPrefix=metadataPrefix,
                 **kwargs):
            fp =  os.path.join(self._dir,
                               "{0}.{1}.xml".format(header.identifier(),
                                                    metadataPrefix)
                               )
            logger.debug('Writing to file {0}'.format(fp))
            with open(fp, 'w') as fh:
                fh.write(metadata)


def main(argv=None):
    '''Command line options.'''
    global argparser, metadata_registry
    if argv is None:
        args = argparser.parse_args()
    else:
        args = argparser.parse_args(argv)
    if args.dir:
        harvester = DirectoryOAIHarvester(metadata_registry,
                                          os.path.abspath(args.dir))
    logger = logging.getLogger(__name__).getChild('main')
    # Parse from and until into datetime objects
    if args.from_ is not None:
        args.from_ = datetime.strptime(args.from_, "%Y-%m-%d")
    if args.until is not None:
        args.until = datetime.strptime(args.until, "%Y-%m-%d")
    for provider in args.provider:
        logger.info('Harvesting from {0}'.format(provider))
        if not provider.startswith('http://'):
            # Fetch configuration from persistent storage
            # Allow over-ride of default metadataPrefix
            logger.critical('Named providers not yet implemented')
            return 1
        else:
            baseUrl = provider
            if args.dir is None:
                args.dir = '.'

        if args.metadataPrefix is None:
            args.metadataPrefix = 'oai_dc'
        harvester.harvest(baseUrl,
                          args.metadataPrefix,
                          from_=args.from_,
                          until=args.until
                          )


# Set up argument parser
docbits = __doc__.split('\n\n')

argparser = ArgumentParser("harvest(.py)",
                           description=docbits[0],
                           epilog='\n\n'.join(docbits[-2:]))
argparser.add_argument('--db', '--database',
                       action='store', dest='databasePath',
                       default=os.path.expanduser('~/.oai-harvest/config.db'),
                       help=("Path to database used for making provider "
                             "configurations persistent.")
                       )
argparser.add_argument('provider',
                       action='store',
                       nargs='+',
                       help="OAI-PMH Provider from which to harvest."
                       )
argparser.add_argument('-p', '--metadataPrefix',
                       action='store', dest='metadataPrefix',
                       default=None,
                       help=("the metadataPrefix of the format (XML Schema) "
                             "in which records should be harvested.")
                       )
argparser.add_argument("-f", "--from", dest="from_",
                       default=None,
                       metavar="YYYY-MM-DD",
                       help=("harvest only records added/modified after this "
                             "date.")
                       )
argparser.add_argument("-u", "--until", dest="until",
                       default=None,
                       metavar="YYYY-MM-DD",
                       help=("harvest only records added/modified up to this "
                             "date.")
                       )

group = argparser.add_mutually_exclusive_group()
group.add_argument('-d', '--dir',
                   action='store', dest='dir',
                   default=None,
                   help=("where to output files for harvested records."
                         "default: current working path")
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
