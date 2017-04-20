# -*- coding: utf-8 -*-
"""TODO: Document test_harvest here.

Copyright (C) 2017, Auto Trader UK
Created 19. Apr 2017 17:42
Creator: john.harrison

"""
import os
import shutil
import unittest
from tempfile import mkdtemp
from uuid import uuid4

from mock import Mock, patch
from oaipmh.common import Header, Metadata
from oaipmh.metadata import MetadataRegistry

from oaiharvest.exceptions import NotOAIPMHBaseURLException
from oaiharvest.harvest import OAIHarvester, DirectoryOAIHarvester


class DirectoryOAIHarvesterrTestCase(unittest.TestCase):

    def setUp(self):
        self.md_registry = Mock(spec_set=MetadataRegistry)
        self.dir_path = mkdtemp()
        self.harvester = DirectoryOAIHarvester(
            self.md_registry,
            self.dir_path
        )

    def tearDown(self):
        shutil.rmtree(self.dir_path)

    def test_init(self):
        harvester = DirectoryOAIHarvester(
            self.md_registry,
            self.dir_path,
            respectDeletions=False,
            createSubDirs=True,
            nRecs=10
        )
        self.assertIsInstance(harvester, OAIHarvester)
        self.assertEqual(harvester._dir, self.dir_path)
        self.assertFalse(harvester.respectDeletions)
        self.assertTrue(harvester.createSubDirs)
        self.assertEqual(harvester.nRecs, 10)

    def test_init_defaults(self):
        self.assertIsInstance(self.harvester, OAIHarvester)
        self.assertEqual(self.harvester._dir, self.dir_path)
        self.assertTrue(self.harvester.respectDeletions)
        self.assertFalse(self.harvester.createSubDirs)
        self.assertEqual(self.harvester.nRecs, 0)

    @patch('oaiharvest.harvest.Client')
    def test_listRecords_on_non_OAI_target(self, MockClient):
        client = MockClient.return_value
        client.identify.side_effect = IndexError
        url = 'https://www.example.com'

        with self.assertRaises(NotOAIPMHBaseURLException):
            list(self.harvester._listRecords(url))

    @patch('oaiharvest.harvest.Client')
    def test_listRecords(self, MockClient):
        client = MockClient.return_value
        mock_recs = [(Mock(), Mock(), Mock)]
        client.listRecords.return_value = iter(mock_recs)
        url = 'https://oai.example.com'

        recs = self.harvester._listRecords(
            url,
            metadataPrefix='oai_dc',
            foo='bar'
        )
        for rec, expected in zip(recs, mock_recs):
            self.assertEqual(rec, expected)

        client.listRecords.assert_called_once_with(
            metadataPrefix='oai_dc',
            foo='bar'
        )

    @patch('oaiharvest.harvest.Client')
    def test_harvest(self, MockClient):
        mock_recs = [
            self._make_pyoai_record(),
            self._make_pyoai_record(),
            self._make_pyoai_record(),
        ]
        client = MockClient.return_value
        client.listRecords.return_value = iter(mock_recs)
        url = 'https://oai.example.com'

        self.assertTrue(self.harvester.harvest(url, 'oai_dc'))
        self.assertEqual(
            len(os.listdir(self.dir_path)),
            len(mock_recs)
        )

    # Helpers

    def _make_pyoai_record(self):
        header = Mock(spec_set=Header)
        header.identifier.return_value = uuid4()
        header.isDeleted.return_value = False
        return (
            header,
            "<xml>data</xml>",
            Mock()
        )


if __name__ == '__main__':
    unittest.main()
