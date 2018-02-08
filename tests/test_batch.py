# -*- coding: utf-8 -*-

import os
import server
import json
import mock

from base import TestBase, FakeResponse

class TestBatch(TestBase):

    @mock.patch('lib.input.requests.Session.get')
    def test_batch_get(self, m_get):
        m_get.side_effect = self.m_get

        resp = self.app.post('/batch', data=json.dumps([
                {
                    "method": "GET",
                    "path": "/47/office/laudes/2017-02-06.rss",
                }, {
                    "method": "GET",
                    "path": "/47/office/laudes/2017-02-06.json",
                },
            ]),
            content_type='application/json',
        )
        
        self.assertEqual(207, resp.status_code)
        data = json.loads(resp.data)
        self.assertEqual(2, len(data))

        # Validate first response
        self.assertEqual(200, data[0]['status'])
        self.assertEqual({
            "Content-Length": "21505",
            "ETag": "9bcdc54442a97b294cd29acbab77b197eae787794ab420fbe4690d1db0cd1d04",
            "Content-Type": "application/rss+xml; charset=utf-8"
        }, data[0]['headers'])

    @mock.patch('lib.input.requests.Session.get')
    def test_batch_get_from_cache(self, m_get):
        m_get.side_effect = self.m_get

        resp = self.app.post('/batch', data=json.dumps([
                {
                    "method": "GET",
                    "path": "/47/office/laudes/2017-02-06.rss",
                    "headers": {
                        "If-None-Match": "9bcdc54442a97b294cd29acbab77b197eae787794ab420fbe4690d1db0cd1d04",
                    },
                }, {
                    "method": "GET",
                    "path": "/47/office/laudes/2017-02-06.json",
                    "headers": {
                        "If-None-Match": "9bcdc54442a97b294cd29acbab77b197eae787794ab420fbe4690d1db0cd1d04",
                    },
                },
            ]),
            content_type='application/json',
        )
        
        self.assertEqual(207, resp.status_code)
        data = json.loads(resp.data)
        self.assertEqual(2, len(data))

        # Validate first response
        self.assertEqual(304, data[0]['status'])
        self.assertEqual("",  data[0]['response'])

        # Validate second response
        self.assertEqual(304, data[1]['status'])
        self.assertEqual("",  data[1]['response'])

