# -*- coding: utf-8 -*-
import unittest

from mock import Mock, patch
from oaipmh.metadata import MetadataRegistry

from oaiharvest.exceptions import NotOAIPMHBaseURLException
from oaiharvest.harvesters.base import OAIRecordGetter


class OAIRecordGetterTestCase(unittest.TestCase):
    def setUp(self):
        self.md_registry = Mock(spec_set=MetadataRegistry)
        self.subject = OAIRecordGetter(self.md_registry)

    @patch("oaiharvest.harvesters.base.Client")
    def test_get_records(self, MockClient):
        client = MockClient.return_value
        header = Mock()
        metadata = Mock()
        about = Mock()
        mock_recs = [(header, metadata, about)]
        client.listRecords.return_value = iter(mock_recs)
        url = "https://oai.example.com"

        recs = self.subject.get_records(url, metadataPrefix="oai_dc", foo="bar")
        for rec, expected in zip(recs, mock_recs):
            self.assertEqual(header, rec.header)
            self.assertEqual(metadata, rec.metadata)
            self.assertEqual(about, rec.about)

        client.listRecords.assert_called_once_with(metadataPrefix="oai_dc", foo="bar")

    @patch("oaiharvest.harvesters.base.Client")
    def test_get_records_on_non_OAI_target(self, MockClient):
        client = MockClient.return_value
        client.identify.side_effect = IndexError
        url = "https://www.example.com"

        with self.assertRaises(NotOAIPMHBaseURLException):
            list(self.subject.get_records(url))


if __name__ == "__main__":
    unittest.main()
