import argparse
import re
import json
import sys


def file_lines(file_path):
    with open(file_path) as f:
        return [line.rstrip() for line in f.readlines()]


def read_json(file_path):
    with open(file_path, encoding="utf-8", errors="surrogateescape") as f:
        return json.load(f)["data"]


def yugioh_card_in_string(string, cards_json, card_id_regex, card_name_regex):
    id_match = re.search(card_id_regex, string)
    if id_match is not None:
        for card in cards_json:
            if card["id"] == int(id_match.group(0)):
                return card
        assert False, "Should be unreachable"
    name_match = re.search(card_name_regex, string)
    if name_match is not None:
        for card in cards_json:
            if card["name"].lower() == name_match.group(0).lower():
                return card
        assert False, "Should be unreachable"
    return None


def regex_or(list_of_strings):
    re_str = "(" + "|".join(list_of_strings) + ")"
    return re.compile(re_str, re.IGNORECASE)


def yugioh_card_id_regex(cards_json):
    return regex_or([str(card["id"]) for card in cards_json])


def yugioh_card_name_regex(cards_json):
    return regex_or([card["name"] for card in cards_json])


def ignore_codec_errors(string):
    no_newlines = string.replace("\n", "\\n").replace("\r", "\\r")
    encoded = no_newlines.encode(sys.stdout.encoding, "replace")
    return encoded.decode(sys.stdout.encoding)


def format_output_card_string(card, format_descriptor_str):
    output = []
    for format_char in format_descriptor_str.lower():
        if format_char == "i":
            output.append(str(card.get("id", "")))
        elif format_char == "n":
            output.append(str(ignore_codec_errors(card.get("name", ""))))
        elif format_char == "t":
            output.append(str(card.get("type", "")))
        elif format_char == "a":
            output.append(str(card.get("attribute", "")))
        elif format_char == "r":
            output.append(str(card.get("race", "")))
        elif format_char == "s":
            none_exist = "atk" not in card and "def" not in card
            if none_exist:
                output.append("")
            else:
                attack = str(card.get("atk", "0"))
                defense = str(card.get("def", "0"))
                output.append(attack + "/" + defense)
        elif format_char == "l":
            if "level" in card:
                output.append("Lv" + str(card.get("level")))
            else:
                output.append("")
        elif format_char == "d":
            output.append(ignore_codec_errors(str(card.get("desc", ""))))
            # print(ignore_codec_errors(repr(output[-1])))
        else:
            raise ValueError("Unrecognized format descriptor character \"" +
                             format_char + "\"")
    return output


def input_lines_to_output_lines_dict(input_file_lines,
                                     cards_json,
                                     format_descriptor_str):
    # Generate regexes
    card_id_regex = yugioh_card_id_regex(cards_json)
    card_name_regex = yugioh_card_name_regex(cards_json)

    # First, convert each line to a list of output fields based on card data
    card_lines_to_output_list = dict()
    for line in input_file_lines:
        # Comments and empty lines should be ignored
        if line.startswith("#") or line.startswith("!") or line.strip() == "":
            continue
        card = yugioh_card_in_string(line, cards_json, card_id_regex, card_name_regex)
        if card is not None:
            output = format_output_card_string(card, format_descriptor_str)
            card_lines_to_output_list[line] = output

    # We want to align text within the output string
    # First, find max length per field
    card_lines_to_output_string = dict()
    max_length_per_index = dict()
    for k, v in card_lines_to_output_list.items():
        for index, field in enumerate(v):
            if index not in max_length_per_index:
                max_length_per_index[index] = 0
            length = len(field)
            if length > max_length_per_index[index]:
                max_length_per_index[index] = length

    # Convert each field list to a string, including text alignment
    for k, v in card_lines_to_output_list.items():
        card_lines_to_output_string[k] = ""
        for index, field in enumerate(v):
            # +1 so that they are not right next to each other
            if max_length_per_index[index] == 0:
                # We do not want to adjust an empty field
                # This way we avoid them being one char wide rather than 0
                adjusted_field = ""
            else:
                adjusted_field = field.ljust(max_length_per_index[index] + 1)
            card_lines_to_output_string[k] += adjusted_field

    # Strip away the final spaces on each each line, coming from the ljust
    for k in card_lines_to_output_string:
        card_lines_to_output_string[k] = card_lines_to_output_string[k].rstrip()

    return card_lines_to_output_string


def input_lines_to_output_lines(input_file_lines,
                                cards_json,
                                format_descriptor_str):
    d = input_lines_to_output_lines_dict(input_file_lines,
                                         cards_json,
                                         format_descriptor_str)
    # Putting all lines into a single string before print is faster than
    #   printing line by line
    all_lines = ""
    for line in input_file_lines:
        # Get converted lines if it exists, default to just line
        all_lines += d.get(line, line) + "\n"
    return all_lines.rstrip()   # Strip final newline


def main(input_file, cards_json_file, format_descriptor_str):
    cards_json = read_json(cards_json_file)
    if input_file is None:
        # Read all possible ids
        input_file_lines = []
        for card in cards_json:
            input_file_lines.append(str(card["id"]))
    else:
        input_file_lines = file_lines(input_file)
    print(input_lines_to_output_lines(input_file_lines,
                                      cards_json,
                                      format_descriptor_str))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reformat file containing lines with Yugioh card ids.',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("cards_json_file",
                        help="""A json file containing information about all possible Yugioh cards that the script shall support.
Can be fetched by running fetch_card_info_json.py and piping the output to a file.""")
    parser.add_argument("format_descriptor_string",
                        help="""A string of letters which describe how each column in the output should be formatted.
The following descriptors may be entered:
  i (short for id):          The Yugioh card id.
  n (short for name):        The name of the card.
  t (short for type):        The type of the card (e.g. Flip Monster).
  a (short for attribute):   The attribute of the card (e.g. DARK)
  r (short for race):        The race of the card (e.g. Winged Beast)
  s (short for stats):       The ATK/DEF of the card.
  l (short for level):       The level of the card.
  d (short for description): The text box contents of the card.
""")
    parser.add_argument("-i", "--input_file",
                        help="""Input file to process.
Each line in the file that shall be processed must contain exactly one Yugioh card ID as a substring.
When ommitted, output all possible cards instead.""")
    args = parser.parse_args()
    main(args.input_file, args.cards_json_file, args.format_descriptor_string)
