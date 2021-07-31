import requests
import json
import argparse


def card_info_json():
    response = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php")
    response.raise_for_status()
    return json.dumps(response.json())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fetch info about all cards from db.ygoprodeck.com and print the result.")
    parser.parse_args()
    print(card_info_json())
