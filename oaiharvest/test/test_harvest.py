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


if __name__ == '__main__':
    unittest.main()
