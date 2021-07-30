import decorate_ydk
import unittest
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

    def test_all_intarsld(self):
        output = decorate_ydk.input_lines_to_output_lines(["12345", "6789"],
                                                          example_json(),
                                                          "intarsld")
        self.assertEqual(output, """\
12345 Spongebob Normal Monster WATER Beast 800/900 Lv3 Lives in a pineapple.
6789  Ow        Spell                                  Ouch.""")

    def test_all_intarsld_reverse_order(self):
        output = decorate_ydk.input_lines_to_output_lines(["6789", "12345"],
                                                          example_json(),
                                                          "intarsld")
        self.assertEqual(output, """\
6789  Ow        Spell                                  Ouch.
12345 Spongebob Normal Monster WATER Beast 800/900 Lv3 Lives in a pineapple.""")

    def test_ow_intarsld(self):
        output = decorate_ydk.input_lines_to_output_lines(["6789"],
                                                          example_json(),
                                                          "intarsld")
        self.assertEqual(output, "6789 Ow Spell Ouch.")

    def test_all_intarsld_back_and_forth(self):
        inp = ["12345 Spongebob Normal Monster WATER Beast 800/900 Lv3 Lives in a pineapple.",
               "6789  Ow        Spell                                  Ouch."]
        output = decorate_ydk.input_lines_to_output_lines(inp,
                                                          example_json(),
                                                          "i")
        self.assertEqual(output, "12345\n6789")

    def test_ow_innnn(self):
        output = decorate_ydk.input_lines_to_output_lines(["6789"],
                                                          example_json(),
                                                          "innnn")
        self.assertEqual(output, "6789 Ow Ow Ow Ow")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(DecorateYdkTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
