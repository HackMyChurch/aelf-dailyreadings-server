import mock

from base import TestBase

EXPECTED_ETAG = '00adc5f88631215ef56c19b7036269524165716034cf4b75a98dd8c0747d47b6'

class TestCache(TestBase):

    @mock.patch('lib.input.requests.Session.get')
    def test_get_laudes_47(self, m_get):
        m_get.side_effect = self.m_get

        # Warm up cache
        resp = self.app.get('/47/office/laudes/2018-01-28.json')
        self.assertEqual(200, resp.status_code)
        self.assertEqual((EXPECTED_ETAG, False), resp.get_etag())

        # Test cache miss
        resp = self.app.get("/47/office/laudes/2018-01-28.json", headers={"If-None-Match": '"miss"'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual((EXPECTED_ETAG, False), resp.get_etag())

        # Test cache hit
        resp = self.app.get("/47/office/laudes/2018-01-28.json", headers={"If-None-Match": f'"{EXPECTED_ETAG}"'},)
        self.assertEqual(304, resp.status_code)

