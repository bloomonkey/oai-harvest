# -*- coding: utf-8 -*-
import os
import shutil
import unittest
from tempfile import mkdtemp
from uuid import uuid4

from mock import Mock, patch
from oaipmh.common import Header
from oaipmh.metadata import MetadataRegistry
from six import PY3

from oaiharvest.harvesters.base import OAIHarvester
from oaiharvest.harvesters.directory_harvester import DirectoryOAIHarvester
from oaiharvest.stores.directory_store import DirectoryRecordStore


class DirectoryOAIHarvesterTestCase(unittest.TestCase):
    def setUp(self):
        self.md_registry = Mock(spec_set=MetadataRegistry)
        self.dir_path = mkdtemp()
        self.harvester = DirectoryOAIHarvester(self.md_registry, self.dir_path)

    def tearDown(self):
        shutil.rmtree(self.dir_path)

    def test_init(self):
        harvester = DirectoryOAIHarvester(
            self.md_registry,
            self.dir_path,
            respectDeletions=False,
            createSubDirs=True,
            nRecs=10,
        )
        self.assertIsInstance(harvester, OAIHarvester)
        self.assertEqual(harvester.nRecs, 10)
        self.assertFalse(harvester.respectDeletions)

        self.assertIsInstance(harvester.store, DirectoryRecordStore)
        self.assertEqual(harvester.store.directory, self.dir_path)
        self.assertTrue(harvester.store.createSubDirs)

    def test_init_defaults(self):
        self.assertIsInstance(self.harvester, OAIHarvester)
        self.assertTrue(self.harvester.respectDeletions)
        self.assertEqual(self.harvester.nRecs, 0)

    @patch("oaiharvest.harvesters.base.Client")
    def test_harvest(self, MockClient):
        mock_recs = [
            self._make_pyoai_record(),
            self._make_pyoai_record(),
            self._make_pyoai_record(),
        ]
        client = MockClient.return_value
        client.listRecords.return_value = iter(mock_recs)
        url = "https://oai.example.com"

        self.assertTrue(self.harvester.harvest(url, "oai_dc"))
        self.assertEqual(len(os.listdir(self.dir_path)), len(mock_recs))

    # Helpers

    def _make_pyoai_record(self):
        header = Mock(spec_set=Header)
        header.identifier.return_value = uuid4()
        header.isDeleted.return_value = False
        if PY3:
            body = "<xml>data ü</xml>"
        else:
            body = u"<xml>data ü</xml>"

        return (header, body, Mock())


if __name__ == "__main__":
    unittest.main()
