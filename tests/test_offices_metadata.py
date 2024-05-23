import datetime
import mock
from base import TestBase

class TestChecksums(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_nominal(self, m_get):
        m_get.side_effect = self.m_get

        # Prepare expectations
        expected_dates_keys = ['2024-05-10', '2024-05-11']
        expected_office_keys = ["complies", "informations", "laudes", "lectures", "messes", "none", "sexte", "tierce", "vepres"]
        expected_metadata_keys = ['checksum', 'generation-date']

        # Get checksums
        resp = self.app.get('/76/offices/metadata/2024-05-10/2d')
        assert resp.status_code == 200
        data: dict[str, dict[str, dict[str, str]]] = resp.json

        # Validate Json structure
        assert list(data.keys()) == expected_dates_keys

        for days_checksums in data.values():
            # Expected offices
            assert list(days_checksums.keys()) == expected_office_keys

            for office_checksum in days_checksums.values():
                # Expected keys
                assert list(office_checksum.keys()) == expected_metadata_keys

                # Checksum looks like a checksum
                assert len(office_checksum['checksum']) == 64

                # Date looks like a date and less than 1h in the past ?
                generation_date = datetime.datetime.fromisoformat(office_checksum['generation-date'])
                assert (datetime.datetime.now(datetime.UTC) - generation_date).total_seconds() < 3600

    @mock.patch('lib.input.requests.Session.get')
    def test_args_validation(self, m_get):
        m_get.side_effect = self.m_get

        # Invalid durations
        assert 404 == self.app.get('/76/offices/metadata/2024-05-10/-2d').status_code
        assert 400 == self.app.get('/76/offices/metadata/2024-05-10/0d').status_code
        assert 400 == self.app.get('/76/offices/metadata/2024-05-10/8d').status_code

        # Invalid date
        assert 400 == self.app.get('/76/offices/metadata/2024-00-00/7d').status_code
        assert 400 == self.app.get('/76/offices/metadata/2024-05-10-/7d').status_code

    @mock.patch('lib.input.requests.Session.get')
    def test_nominal_office_headers(self, m_get):
        m_get.side_effect = self.m_get

        # Get mass
        resp = self.app.get('/76/office/messes/2024-05-10.json')
        assert 200 == resp.status_code

        # Validate headers
        assert ('c1a8d3dad105608e0a207b1ec8820a1d99f296c269cf7d766fad0e81db46243d', False) == resp.get_etag()
        assert resp.last_modified is not None
        assert (datetime.datetime.now(datetime.UTC) - resp.last_modified).total_seconds() < 3600 # type: ignore
