import fetch_card_info_json
import unittest
import unittest.mock


class FetchCardInfoJsonTests(unittest.TestCase):

    def test_card_info_json(self):

        def mocked_requests_get(*args, **kwargs):
            class MockResponse:
                def __init__(self, json_data, status_code):
                    self.json_data = json_data
                    self.status_code = status_code

                def json(self):
                    return self.json_data

                def raise_for_status(self):
                    pass

            if args[0] == "https://db.ygoprodeck.com/api/v7/cardinfo.php":
                return MockResponse({"name": "Seto Kaiba"}, 200)
            return MockResponse(None, 404)

        with unittest.mock.patch('requests.get', side_effect=mocked_requests_get) as request_m:
            output = fetch_card_info_json.card_info_json()
            self.assertEqual(output, "{\"name\": \"Seto Kaiba\"}")
            request_m.assert_called_once_with("https://db.ygoprodeck.com/api/v7/cardinfo.php")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(FetchCardInfoJsonTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
