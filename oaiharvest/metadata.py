"""Metadata handling classes."""

import logging

from oaipmh.metadata import MetadataRegistry
from lxml.etree import tostring
import six

class DefaultingMetadataRegistry(MetadataRegistry):
    """MetadataRegistry with default reader and/or writer.

    MetadataRegistry that can be init'd with a default reader and/or writer.
    """

    def __init__(self, defaultReader=None, defaultWriter=None):
        MetadataRegistry.__init__(self)
        self.defaultReader = defaultReader
        self.defaultWriter = defaultWriter

    def readMetadata(self, metadata_prefix, element):
        try:
            return MetadataRegistry.readMetadata(self,
                                                 metadata_prefix,
                                                 element)
        except KeyError as key_error:
            try:
                return self.defaultReader(element)
            except AttributeError:
                raise key_error

    def writeMetadata(self, metadata_prefix, element, metadata):
        try:
            return MetadataRegistry.writeMetadata(self,
                                                  metadata_prefix,
                                                  element,
                                                  metadata
                                                  )
        except KeyError as key_error:
            try:
                return self.defaultWriter(element, metadata)
            except AttributeError:
                raise key_error


class XMLMetadataReader(object):
    """Really simple MetadataReader to serialize metadata to pretty XML."""
    def __call__(self, metadata_element):
        # Six call fixes 'sequence item 0: expected str instance, bytes found'
        return '\n'.join(
          [six.text_type(
              tostring(rec_element,
                    method="xml",
                    pretty_print=True))
           for rec_element
           in metadata_element])
