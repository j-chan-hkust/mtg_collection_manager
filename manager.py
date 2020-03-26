import os
import pandas as pd
import requests
import time
from datetime import date
from difflib import SequenceMatcher

# walk through the file list in "new additions" directory
# load the existing inventory list from the generated excel
# combine existing inventory with new additions
# fill in auxiliary data, if and only if the age of the data is too old +2 weeks
# using the scryfall api
# print out the file to an excel dock

# todo add check for foiling
# todo add check for name
# todo handle formatting issues when writing to excel
# todo if completely rewrites the excel file, need to fix that
# todo convert price text to number
# todo add low-quality images into the excel file


# used to access string similarity
def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# queries scryfall and returns the result in a json, which in python is formatted as a dictionary
def query_scryfall_for_json(card_name):
    return requests.get(
        "https://api.scryfall.com/cards/search?q=" + card_name.replace(' ', '+') + "&unique=prints").json()


# using the data from our input,
# todo because which edition we get is contingent on information on the foiling,
#  i think its best to perform filtering and data updating in a single step
#  its too much of an interlinked process.
def filter_for_card_data(input_data, card_list):
    # todo at the moment - you have to perfectly input the set code, and doesn't handle this error for the user
    if 'Set' in input_data and len(input_data['Set']) != 0:
        for card in card_list:
            if card['set'].upper() == input_data['Set'].upper().strip() \
                    and similar(card['name'], input_data['Name']) > 0.9:
                return card
    else:
        min = float('inf')
        temp = {}
        for card in card_list:
            if card['prices']['usd'] is not None and similar(card['name'], input_data['Name']) > 0.9:
                if float(card['prices']['usd']) < min:
                    min = float(card['prices']['usd'])
                    temp = card
        return temp


# adds relevant data to the card in question
# THIS FUNCTION CHANGES THE DATA!
def update_card_data(card_to_update, card_data_to_add, foil=False):
    card_to_update['Set'] = card_data_to_add['set'].upper()
    card_to_update['Price'] = card_data_to_add['prices']['usd']
    card_to_update['Name'] = card_data_to_add['name']
    card_to_update['last_accessed'] = date.today().strftime('%d/%m/%Y')


# todo instead of concatenating to a dictionary, and then finally updating, we're going to be
#   updating the excel file directly using an excel writer. This preserves formatting, and means
#   we don't rewrite the original file. The issue I see is having to deal with a lot of finicky column
#   management, that was previously automated by the pandas lib.
def update_excel(excelWriter, card_data):
    return None


def manage():

    dfs = pd.read_excel('Full collection.xlsx', sheet_name=None)
    for df in dfs:
        print(dfs[df].head())

    # todo this will be an implementation of the specific case of full collection, I will make this generic in future

    input_card_list = dfs["FULL COLLECTION"].fillna('').to_dict('records')  # this converts it into list of dictionaries

    output_card_list = []

    for input_card in input_card_list:
        print("getting... " + input_card["Name"])
        start = time.time()

        # get list of all editions from scryfall
        response_json = query_scryfall_for_json(input_card["Name"])

        if response_json['object'] == 'error':
            print("uh oh, you made a typo for card " + input_card["Name"] + ", and we can't find it!")
            print("we've left the card as is...")
            output_card_list.append(input_card)
            continue

        card_response_data = response_json['data']

        card_data = filter_for_card_data(input_card, card_response_data)

        update_card_data(input_card, card_data)

        print(input_card)

        # todo i don't think output is even needed now lol, output_card_list should = input_list
        output_card_list.append(input_card)

        # todo query can be made more efficient
        print("time taken for this query is (in ms):")
        print(time.time() - start)

    pd.DataFrame(output_card_list).to_excel("Full collection.xlsx", sheet_name="FULL COLLECTION")


if __name__ == "__main__":
    manage()
