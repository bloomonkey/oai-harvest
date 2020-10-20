# -*- coding: utf-8 -*-
"""Document directory_store here.

Copyright (C) 2020, Auto Trader UK
Created 01. Jul 2020 22:14

"""
import codecs
import logging
import os
import platform

from six import string_types
from six.moves.urllib import parse as urllib

from oaiharvest.record import Record


class DirectoryRecordStore(object):
    def __init__(self, directory, createSubDirs=False):
        self.directory = directory
        self.createSubDirs = createSubDirs
        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__)

    def write(self, record: Record, metadataPrefix: str):
        fp = self._get_output_filepath(record.header, metadataPrefix)
        self._ensure_dir_exists(fp)
        self.logger.debug("Writing to file {0}".format(fp))
        with codecs.open(fp, "w", encoding="utf-8") as fh:
            fh.write(record.metadata)

    def delete(self, record: Record, metadataPrefix: str):
        fp = self._get_output_filepath(record.header, metadataPrefix)
        try:
            os.remove(fp)
        except OSError:
            # File probably does't exist in destination directory
            # No further action needed
            self.logger.debug("")
            pass

    def _get_output_filepath(self, header, metadataPrefix):
        filename = "{0}.{1}.xml".format(header.identifier(), metadataPrefix)

        protected = []
        if platform.system() != "Windows":
            protected.append(":")

        if self.createSubDirs:
            if isinstance(self.createSubDirs, string_types):
                # Replace specified character with platform path separator
                filename = filename.replace(self.createSubDirs, os.path.sep)

            # Do not escape path separators, so that sub-directories
            # can be created
            protected.append(os.path.sep)

        filename = urllib.quote(filename, "".join(protected))
        fp = os.path.join(self.directory, filename)
        return fp

    def _ensure_dir_exists(self, fp):
        if not os.path.isdir(os.path.dirname(fp)):
            # Missing base directory or sub-directory
            self.logger.debug("Creating target directory {0}".format(self.directory))
            os.makedirs(os.path.dirname(fp))
