import datetime
import mock
from base import TestBase

class TestChecksums(TestBase):
    @mock.patch('lib.input.requests.Session.get')
    def test_nominal(self, m_get):
        m_get.side_effect = self.m_get

        # Prepare expectations
        expected = {
            "2024-05-10": {
                "complies": {"checksum": "f2d597017f760488a83c43883e9fb791c4ed5e775c69379a6dd4cfe52e49f370"},
                "informations": {"checksum": "1a29978b58c5cc239d4ab05939209cb7f206a16d09f029a089be2bba9ef8e01d"},
                "laudes": {"checksum": "b31d90de829310d8150fefb441c7c18c500b85a7e1d5dbc0ef3b545d29461836"},
                "lectures": {"checksum": "00b2429cec47d047a28097791d4bf64bc772c1909339702db6384be014f621d9"},
                "messes": {"checksum": "dcefeb7f58e77da32cd096da89485058f473fff38ec0a0c85cec9fc8b1340431"},
                "none": {"checksum": "032c3ea9c9348fe5f318f9058c83a559022e47bef5a5327057805ac63ee064ad"},
                "sexte": {"checksum": "300c1cc1501cc009c4285221527bf0b3aeaed99135d6dee86fb782af84947e9f"},
                "tierce": {"checksum": "cc0f6abb73f25d8868bccdd525678db8208b5ef4b3a86bd78ce6f4d264cf0115"},
                "vepres": {"checksum": "90bff018e0e11ec16212f8b91730726db7905a6737a70666dde32337a840df25"}
            },
            "2024-05-11": {
                "complies": {"checksum": "9865729b699ac6a83af53da9822e4a6c7642a5144c7e7648f4e782da864eade4"},
                "informations": {"checksum": "b0f84358b533fddb7eb5d6466e0d57c5d6adedfda40dc785f4f59ba8f153ad9e"},
                "laudes": {"checksum": "1797a1fa1b71c4cd791b2d0d55538f4f6b4b157495c8cfc36e7377e462cd8ba9"},
                "lectures": {"checksum": "e86df3882c50796e17422f569dc3ba155801b8de97544d7908eed73d372f5e86"},
                "messes": {"checksum": "8f8a88273ee7f74b39d83519e7057ade1713f054b463b86c3e4b964b1b8d3d6d"},
                "none": {"checksum": "f98a0206a176a18ccb24e517b57ba65da97aa51fe20667f161c80c8248027009"},
                "sexte": {"checksum": "f1f7a60993ab548ac5d7ccc99827362273d332fa4d1eb0bbf6d87adb370f8f14"},
                "tierce": {"checksum": "92a9b250a63d21367242d779ed72379bfb491c4bf6a573d011b1809579a645ea"},
                "vepres": {"checksum": "9f368bfb6eccd6226fa0d2f49c508aec084d0739e1a05b7242cf191c5ce2298e"}
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
                    expected[day][office_name]['checksum'],
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
        resp = self.app.get('/76/office/messes/2024-05-10.json')
        self.assertEqual(200, resp.status_code)

        # Validate headers
        self.assertEqual(('dcefeb7f58e77da32cd096da89485058f473fff38ec0a0c85cec9fc8b1340431', False), resp.get_etag())
        self.assertIsNotNone(resp.last_modified)
        self.assertLess((datetime.datetime.now(datetime.UTC) - resp.last_modified).total_seconds(), 3600) # type: ignore
