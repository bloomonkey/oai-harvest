# -*- coding: utf-8 -*-
"""Document base here.

Copyright (C) 2020, Auto Trader UK
Created 01. Jul 2020 22:03

"""
import ast
import logging
from datetime import datetime, timedelta
from time import sleep

from oaipmh.client import Client

from oaiharvest.exceptions import NotOAIPMHBaseURLException
from oaiharvest.record import Record


class OAIHarvester(object):
    """Abstract Base Class for an OAI-PMH Harvester.

    Should be sub-classed in order to do useful things with the harvested
    records (e.g. put them in a directory, VCS repository, local database etc.
    """

    def __init__(self, mdRegistry):
        self._mdRegistry = mdRegistry

    def pause(self, now, until):
        """ Unconditionally pause the process from `now` to `until`. """
        logger = logging.getLogger(__name__).getChild("OAIHarvester.pause")
        logger.info("Pausing until {} (incremental harvest).".format(until))
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
        kwargs["metadataPrefix"] = metadataPrefix
        client = Client(baseUrl, self._mdRegistry)
        incremental_range = kwargs.pop("between", None)
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
            yield Record(header, metadata, about)
            self.maybe_pause_if_incremental(incremental_range)

    def harvest(self, baseUrl, metadataPrefix, **kwargs):
        "Harvest records"
        raise NotImplementedError(
            "{0.__class__.__name__} must be sub-classed".format(self)
        )
