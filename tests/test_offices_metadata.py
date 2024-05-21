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
                "lectures": {"checksum": "d6039c96b28c4c09f66cf72bc7e280fe823190f768dc17e7f371e8db2d209150"},
                "messes": {"checksum": "dcefeb7f58e77da32cd096da89485058f473fff38ec0a0c85cec9fc8b1340431"},
                "none": {"checksum": "fcc3361fe75d1b7b9958b656d313879b1033409d45d73ea1b272c08e811110d8"},
                "sexte": {"checksum": "69fdda7b511ce23713e5b2a9dcb4b1b5bb749f5d737feb0cb92f847b19a0d63f"},
                "tierce": {"checksum": "a7bfa85687abaa2fc6bb7c8dd86eb1653460dce601a79a21cfccb1e16afbdf8f"},
                "vepres": {"checksum": "90bff018e0e11ec16212f8b91730726db7905a6737a70666dde32337a840df25"}
            },
            "2024-05-11": {
                "complies": {"checksum": "7b7a6774f861dff9aca5fe5a92f5923e6047516b04e49d0c2c5452d6fdc1dd6a"},
                "informations": {"checksum": "b0f84358b533fddb7eb5d6466e0d57c5d6adedfda40dc785f4f59ba8f153ad9e"},
                "laudes": {"checksum": "1797a1fa1b71c4cd791b2d0d55538f4f6b4b157495c8cfc36e7377e462cd8ba9"},
                "lectures": {"checksum": "4e7bb68c3c07c48ff9d2552ef034b085c42be1580cd349a7ab7208f861a45a82"},
                "messes": {"checksum": "8f8a88273ee7f74b39d83519e7057ade1713f054b463b86c3e4b964b1b8d3d6d"},
                "none": {"checksum": "cd41c999e97613a453f8b3811dab0f10bc7be10ce2efe96370e28dc48d534998"},
                "sexte": {"checksum": "0e52c71ca214451abbcbfb2eaedd98925d572ae9ac62a34f2130ecf8699be1eb"},
                "tierce": {"checksum": "aab84089eb33b4df824f8b6d9876be86326e286d2b8598f5b0d682afe5cb34e8"},
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
