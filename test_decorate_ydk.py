import decorate_ydk
import unittest
import unittest.mock
import json

def example_json():
    text = """
{"data": [
{"id": 12345, "name": "Spongebob", "type": "Normal Monster",
"attribute": "WATER", "race": "Beast", "atk": 800, "def": 900, "level": 3,
"desc": "Lives in a pineapple."},
{"id": 6789, "name": "Ow", "type": "Spell", "desc": "Ouch."}
]}
"""
    return json.loads(text)["data"]


class DecorateYdkTests(unittest.TestCase):

    def test_input_lines_to_output_lines_all_intarsld(self):
        output = decorate_ydk.input_lines_to_output_lines(["12345", "6789"],
                                                          example_json(),
                                                          "intarsld")
        self.assertEqual(output, """\
12345 Spongebob Normal Monster WATER Beast 800/900 Lv3 Lives in a pineapple.
6789  Ow        Spell                                  Ouch.""")

    def test_input_lines_to_output_lines_all_intarsld_reverse_order(self):
        output = decorate_ydk.input_lines_to_output_lines(["6789", "12345"],
                                                          example_json(),
                                                          "intarsld")
        self.assertEqual(output, """\
6789  Ow        Spell                                  Ouch.
12345 Spongebob Normal Monster WATER Beast 800/900 Lv3 Lives in a pineapple.""")

    def test_input_lines_to_output_lines_ow_intarsld(self):
        output = decorate_ydk.input_lines_to_output_lines(["6789"],
                                                          example_json(),
                                                          "intarsld")
        self.assertEqual(output, "6789 Ow Spell Ouch.")

    def test_input_lines_to_output_lines_ow_innnn(self):
        output = decorate_ydk.input_lines_to_output_lines(["6789"],
                                                          example_json(),
                                                          "innnn")
        self.assertEqual(output, "6789 Ow Ow Ow Ow")

    def test_input_lines_to_output_lines_all_intarsld_back_and_forth(self):
        inp = ["12345 Spongebob Normal Monster WATER Beast 800/900 Lv3 Lives in a pineapple.",
               "6789  Ow        Spell                                  Ouch."]
        output = decorate_ydk.input_lines_to_output_lines(inp,
                                                          example_json(),
                                                          "i")
        self.assertEqual(output, "12345\n6789")

    def test_input_lines_to_output_lines_ignores_fake_ids(self):
        output = decorate_ydk.input_lines_to_output_lines(["999999999 6789"],
                                                          example_json(),
                                                          "i")
        self.assertEqual(output, "6789")

    def test_input_lines_to_output_lines_finds_names(self):
        output = decorate_ydk.input_lines_to_output_lines(["Woe is Spongebob!"],
                                                          example_json(),
                                                          "i")
        self.assertEqual(output, "12345")

    def test_input_lines_to_output_lines_finds_names_ignores_case(self):
        output = decorate_ydk.input_lines_to_output_lines(["SpOnGeBob"],
                                                          example_json(),
                                                          "i")
        self.assertEqual(output, "12345")

    def test_input_lines_to_output_lines_prioritizes_first_name(self):
        output = decorate_ydk.input_lines_to_output_lines(["Ow Spongebob!"],
                                                          example_json(),
                                                          "i")
        self.assertEqual(output, "6789")

    def test_input_lines_to_output_lines_prioritizes_first_id(self):
        output = decorate_ydk.input_lines_to_output_lines(["123456789"],
                                                          example_json(),
                                                          "i")
        self.assertEqual(output, "12345")

    def test_initialize_cards_json_file_path_input_not_None(self):
        self.assertEqual("foo",
                         decorate_ydk.initialize_cards_json_file_path("foo"))

    def test_initialize_cards_json_file_path_input(self):

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

        with unittest.mock.patch('requests.get', side_effect=mocked_requests_get) as request_m, \
             unittest.mock.patch('builtins.open', unittest.mock.mock_open()) as open_m, \
             unittest.mock.patch('decorate_ydk.default_card_json_file_path', return_value="/foo/bar/baz"):

            output = decorate_ydk.initialize_cards_json_file_path(None)
            self.assertEqual(output, "/foo/bar/baz")
            open_m.assert_called_once_with("/foo/bar/baz", "w")
            request_m.assert_called_once_with("https://db.ygoprodeck.com/api/v7/cardinfo.php")
            open_m.return_value.__enter__().write.assert_called_once_with("{\"name\": \"Seto Kaiba\"}")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(DecorateYdkTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
