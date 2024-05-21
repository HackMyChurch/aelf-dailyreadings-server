import datetime
import mock
from base import TestBase

class TestChecksums(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_nominal(self, m_get):
        m_get.side_effect = self.m_get

        # Prepare expectations
        expected = {
            '2024-05-10': {
                'complies':     '9126bcac0eefe8bed3cd49a886a38000aa1e87410b8342e5dee0661527d78d9f',
                'informations': '1a29978b58c5cc239d4ab05939209cb7f206a16d09f029a089be2bba9ef8e01d',
                'laudes':       '97b42430848f9a2d43c9de7d4f58c5a7c3c6046d2aa25949c7fd09f06c30bf45',
                'lectures':     'ca56f6078058f85e23c21616d937b3d742e208dbb6e7e4d62548e7dd1b45622c',
                'messes':       'dcefeb7f58e77da32cd096da89485058f473fff38ec0a0c85cec9fc8b1340431',
                'none':         'de1eb86e67ca2e297f6248d6bf777779738c6de7196289c3e761ce3a50875adf',
                'sexte':        '0fe63b4686ebca8fcb1e19157d615dd67e798e27f82829239dab88648d456ddb',
                'tierce':       '6451f6c0c9fc490e79adf20e95fbbe8cba6dd0e7c2c1ec227c1e409b17f04c49',
                'vepres':       '4805e480c05f1086f369b0bd59a7eada1f4b43e8f4a4ee9a7cbdb243da88a550',
            },
            '2024-05-11': {
                'complies':     '708f6a4096e24540519369969e5f3872adf9a3a0a7c7cdf440913f0432c436ba',
                'informations': 'b0f84358b533fddb7eb5d6466e0d57c5d6adedfda40dc785f4f59ba8f153ad9e',
                'laudes':       'b3977dd450c93b21da79100870f4160285f0749c4ad5422ee772ece0f81e100c',
                'lectures':     '87133703d763fd725aebb7fe70aebe87135cebeea9cc1bae35ccd170b01327ea',
                'messes':       '8f8a88273ee7f74b39d83519e7057ade1713f054b463b86c3e4b964b1b8d3d6d',
                'none':         'f36f101eeedfa392b2593a8fbe1f1902a22c4b3e8e9947caa4c32a496da27319',
                'sexte':        '2b11bea6b5408b684df827fa4915b4e8b4fcd3e1e30b26341f82396d78bcf517',
                'tierce':       '1d98a248a6e3197423d96dbf7c2b3a8307eb529f77708b72a9bbc9d8694b8835',
                'vepres':       '556fee1ffee76453fd2a40df96a1920ca00deb782bed33c1360df1296438e1fe',
            }
        }

        # Get checksums
        resp = self.app.get('/76/offices/metadata/2024-05-10/2d')
        self.assertEqual(200, resp.status_code)
        data = resp.json

        # Validate Json structure
        self.assertEqual(
            expected.keys(),
            data.keys(),
        )

        for day, days_checksums in data.items():
            self.assertEqual(
                expected[day].keys(),
                days_checksums.keys(),
            )

            for office_name, office_checksum in days_checksums.items():
                # Expected checksum ?
                self.assertEqual(
                    expected[day][office_name],
                    office_checksum['checksum'],
                )

                # Date looks like a date and less than 1h in the past ?
                generation_date = datetime.datetime.fromisoformat(office_checksum['generation-date'])
                self.assertLess((datetime.datetime.now(datetime.UTC) - generation_date).total_seconds(), 3600)

    @mock.patch('lib.input.requests.Session.get')
    def test_args_validation(self, m_get):
        m_get.side_effect = self.m_get

        # Invalid durations
        self.assertEqual(404, self.app.get('/76/offices/metadata/2024-05-10/-2d').status_code)
        self.assertEqual(400, self.app.get('/76/offices/metadata/2024-05-10/0d').status_code)
        self.assertEqual(400, self.app.get('/76/offices/metadata/2024-05-10/8d').status_code)

        # Invalid date
        self.assertEqual(400, self.app.get('/76/offices/metadata/2024-00-00/7d').status_code)
        self.assertEqual(400, self.app.get('/76/offices/metadata/2024-05-10-/7d').status_code)

    @mock.patch('lib.input.requests.Session.get')
    def test_nominal_office_headers(self, m_get):
        m_get.side_effect = self.m_get

        # Get mass
        resp = self.app.get('/76/office/messes/2024-05-10')
        self.assertEqual(200, resp.status_code)

        # Validate headers
        self.assertEqual(('dcefeb7f58e77da32cd096da89485058f473fff38ec0a0c85cec9fc8b1340431', False), resp.get_etag())
        self.assertIsNotNone(resp.last_modified)
        self.assertLess((datetime.datetime.now(datetime.UTC) - resp.last_modified).total_seconds(), 3600) # type: ignore
