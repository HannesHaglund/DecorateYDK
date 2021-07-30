import argparse
import re
import json
import sys

def file_lines(file_path):
    with open(file_path) as f:
        return [l.rstrip() for l in f.readlines()]

def read_json(file_path):
    with open(file_path, encoding="utf-8", errors="surrogateescape") as f:
        return json.load(f)["data"]

def numbers_in_string(string):
    return [int(s) for s in re.findall('\d+', string)]

def yugioh_id_candidate_in_string(string):
    nums = numbers_in_string(string)
    if nums:
        return max(nums)
    else:
        return None

def card_from_id(card_id, available_cards):
    # TODO: This could be sped up by using a dict over a list for available cards
    for card in available_cards:
        if card["id"] == card_id:
            return card
    return None

def are_elements_unique(container):
    return (len(list(set(container))) == len(container))

def format_output_card_string(card, format_descriptor_str):
    if not "i" in format_descriptor_str.lower():
        raise ValueError("Format descriptor string must contain at least one \"i\"")
    output = []
    for format_char in format_descriptor_str.lower():
        if   format_char == "i": output.append(str(card.get("id")))
        elif format_char == "n": output.append(str(card.get("name")))
        elif format_char == "t": output.append(str(card.get("type")))
        elif format_char == "a": output.append(str(card.get("attribute")))
        elif format_char == "r": output.append(str(card.get("race")))
        elif format_char == "s": output.append(str(card.get("atk")) + "/" + str(card.get("def")))
        elif format_char == "l": output.append("Lv" + str(card.get("level")))
        elif format_char == "d": output.append(str(card.get("desc")).replace("\n", " "))
        else: raise ValueError("Unrecognized format descriptor character \"" + format_char + "\"")
    return output



def input_lines_to_output_lines_dict(input_file_lines, cards_json_file, format_descriptor_str):

    cards_db = read_json(cards_json_file)

    # First, convert each line to a list of output fields based on card data
    card_lines_to_output_list = dict()
    for line in input_file_lines:
        # Comments and empty lines should be ignored
        if line.startswith("#") or line.startswith("!") or line.strip() == "":
            continue
        card = card_from_id(yugioh_id_candidate_in_string(line), cards_db)
        if card is not None:
            card_lines_to_output_list[line] = format_output_card_string(card, format_descriptor_str)

    # We want to align text within the output string
    # First, find max length per field
    card_lines_to_output_string = dict()
    max_length_per_index = dict()
    for k,v in card_lines_to_output_list.items():
        for index,field in enumerate(v):
            if index not in max_length_per_index:
                max_length_per_index[index] = 0
            length = len(field)
            if length > max_length_per_index[index]:
                max_length_per_index[index] = length

    # Convert each field list to a string, including text alignment
    for k,v in card_lines_to_output_list.items():
        card_lines_to_output_string[k] = ""
        for index,field in enumerate(v):
            # +1 so that they are not right next to each other
            card_lines_to_output_string[k] += field.ljust(max_length_per_index[index] + 1)

    return card_lines_to_output_string

def ignore_codec_errors(string):
    return string.encode(sys.stdout.encoding, "replace").decode(sys.stdout.encoding)

def main(input_file, cards_json_file, format_descriptor_str):
    foo = 22
    if input_file is None:
        # Read all possible ids
        input_file_lines = []
        cards_db = read_json(cards_json_file)
        for card in cards_db:
            input_file_lines.append(str(card["id"]))
    else:
        input_file_lines = file_lines(input_file)
    d = input_lines_to_output_lines_dict(input_file_lines, cards_json_file, format_descriptor_str)
    # Putting all lines into a single string before print is faster than printing line by line
    all_lines = ""
    for line in input_file_lines:
        if line in d:
            all_lines += ignore_codec_errors(d[line]) + "\n"
        else:
            all_lines += ignore_codec_errors(line) + "\n"
    print(all_lines)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reformat file containing lines with yugioh card ids.',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("cards_json_file",
                        help="A json file containing information about all possible Yugioh cards that the script shall support.")
    parser.add_argument("format_descriptor_str",
                        help=\
                        """A string of letters which describe how each column in the output should be formatted.
The following descriptors may be entered:
  i (short for id):          The Yugioh card id. NOTE: This descriptor must be used at least once for the format_descriptior_string to be valid.
  n (short for name):        The name of the card.
  t (short for type):        The type of the card (e.g. Flip Monster).
  a (short for attribute):   The attribute of the card (e.g. DARK)
  r (short for race):        The race of the card (e.g. Winged Beast)
  s (short for stats):       The ATK/DEF of the card.
  l (short for level):       The level of the card.
  d (short for description): The text box contents of the card.
""")
    parser.add_argument("-f", "--input_file",
                        help="Input file to process. If ommitted, output all possible cards instead. Each line in the file that shall be processed must contain exactly one Yugioh card ID as a substring.")
    args = parser.parse_args()
    main(args.input_file, args.cards_json_file, args.format_descriptor_str)
