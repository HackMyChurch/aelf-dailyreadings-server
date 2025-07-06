import mock

from base import TestBase

EXPECTED_ETAG = "f948b03830e4ff4c6e70fea6903eb5d4fd15576d975d315431bf34ba8eef02ac"

class TestCache(TestBase):

    @mock.patch('lib.input.requests.Session.get')
    def test_get_laudes(self, m_get):
        m_get.side_effect = self.m_get

        # Warm up cache
        resp = self.app.get("/76/office/laudes/2025-08-02.json")
        self.assertEqual(200, resp.status_code)
        self.assertEqual((EXPECTED_ETAG, False), resp.get_etag())

        # Test cache miss
        resp = self.app.get(
            "/76/office/laudes/2025-08-02.json", headers={"If-None-Match": '"miss"'}
        )
        self.assertEqual(200, resp.status_code)
        self.assertEqual((EXPECTED_ETAG, False), resp.get_etag())

        # Test cache hit
        resp = self.app.get(
            "/76/office/laudes/2025-08-02.json",
            headers={"If-None-Match": f'"{EXPECTED_ETAG}"'},
        )
        self.assertEqual(304, resp.status_code)

