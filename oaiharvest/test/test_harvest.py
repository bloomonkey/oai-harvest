# -*- coding: utf-8 -*-
"""TODO: Document test_harvest here.

Copyright (C) 2017, Auto Trader UK
Created 19. Apr 2017 17:42
Creator: john.harrison

"""

import unittest
from tempfile import TemporaryDirectory

from mock import Mock, patch
from oaipmh.metadata import MetadataRegistry

from oaiharvest.exceptions import NotOAIPMHBaseURLException
from oaiharvest.harvest import OAIHarvester, DirectoryOAIHarvester


class DirectoryOAIHarvesterrTestCase(unittest.TestCase):

    def setUp(self):
        self.md_registry = Mock(spec_set=MetadataRegistry)
        self.direcory = TemporaryDirectory()
        self.harvester = DirectoryOAIHarvester(
            self.md_registry,
            self.direcory.name
        )

    def tearDown(self):
        self.direcory.cleanup()

    def test_init(self):
        with TemporaryDirectory() as dir_path:
            harvester = DirectoryOAIHarvester(
                self.md_registry,
                dir_path,
                respectDeletions=False,
                createSubDirs=True,
                nRecs=10
            )
            self.assertIsInstance(harvester, OAIHarvester)
            self.assertEqual(harvester._dir, dir_path)
            self.assertFalse(harvester.respectDeletions)
            self.assertTrue(harvester.createSubDirs)
            self.assertEqual(harvester.nRecs, 10)

    def test_init_defaults(self):
        self.assertIsInstance(self.harvester, OAIHarvester)
        self.assertEqual(self.harvester._dir, self.direcory.name)
        self.assertTrue(self.harvester.respectDeletions)
        self.assertFalse(self.harvester.createSubDirs)
        self.assertEqual(self.harvester.nRecs, 0)

    @patch('oaiharvest.harvest.Client')
    def test_listRecords_on_non_OAI_target(self, MockClient):
        client = MockClient.return_value
        client.identify.side_effect = IndexError
        url = 'https://www.example.com'

        with self.assertRaises(NotOAIPMHBaseURLException):
            for rec in self.harvester._listRecords(url):
                pass

    @patch('oaiharvest.harvest.Client')
    def test_listRecords(self, MockClient):
        client = MockClient.return_value
        mock_recs = [Mock()]
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


if __name__ == '__main__':
    unittest.main()
