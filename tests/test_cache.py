import mock

from base import TestBase

EXPECTED_ETAG = 'ceffc3fead459bf87711d65b3d34f0aee123521af54f64fd44aee5782a5bdfd7'

class TestCache(TestBase):

    @mock.patch('lib.input.requests.Session.get')
    def test_get_laudes_47(self, m_get):
        m_get.side_effect = self.m_get

        # Warm up cache
        resp = self.app.get('/47/office/laudes/2018-01-28')
        self.assertEqual(200, resp.status_code)
        self.assertEqual((EXPECTED_ETAG, False), resp.get_etag())

        # Test cache miss
        resp = self.app.get('/47/office/laudes/2018-01-28', headers={'If-None-Match': '"miss"'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual((EXPECTED_ETAG, False), resp.get_etag())

        # Test cache hit
        resp = self.app.get('/47/office/laudes/2018-01-28', headers={'If-None-Match': f'"{EXPECTED_ETAG}"'})
        self.assertEqual(304, resp.status_code)

