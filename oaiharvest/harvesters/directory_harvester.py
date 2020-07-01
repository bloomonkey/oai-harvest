# -*- coding: utf-8 -*-
"""Document directory_harvester here.

Copyright (C) 2020, Auto Trader UK
Created 01. Jul 2020 22:03

"""
import codecs
import logging
import os
import platform

from six import string_types

from oaiharvest.record import Record
from oaiharvest.harvesters.base import OAIHarvester
from oaiharvest.stores.directory_store import DirectoryRecordStore


class DirectoryOAIHarvester(OAIHarvester):
    """OAI-PMH Harvester to output harvested records to files in a directory.

    Directory to output files to is specified at object init/construction
    time.
    """

    def __init__(self, mdRegistry, directory,
                 respectDeletions=True, createSubDirs=False, nRecs=0):
        OAIHarvester.__init__(self, mdRegistry)
        self.store = DirectoryRecordStore(directory, createSubDirs)
        self.respectDeletions = respectDeletions
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
        for record in self._listRecords(
                 baseUrl,
                 metadataPrefix=metadataPrefix,
                 **kwargs):

            if self.nRecs and self.nRecs > 0 and self.nRecs <= i:
                logger.info("Stopping harvest; set limit of {0} has been "
                            "reached".format(self.nRecs))
                break

            if not record.header.isDeleted():
                self.store.write(record, metadataPrefix)
                i += 1
            else:
                if self.respectDeletions:
                    logger.debug(
                        "Respecting server request to delete record {0}.{1}".format(
                            record.identifier, metadataPrefix
                        )
                    )
                    self.store.delete(record, metadataPrefix)
                else:
                    logger.debug(
                        "Ignoring server request to delete file {0}.{1}".format(
                            record.identifier, metadataPrefix
                        )
                    )
        else:
            # Harvesting completed, all available records stored
            return True
        # Loop must have been stopped with ``break``, e.g. due to
        # arbitrary limit
        return False