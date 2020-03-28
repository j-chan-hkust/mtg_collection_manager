import pandas as pd
import time
from datetime import date
from datetime import datetime as dt
from difflib import SequenceMatcher

import pandas as pd
import requests


# walk through the file list in "new additions" directory
# load the existing inventory list from the generated excel
# combine existing inventory with new additions
# fill in auxiliary data, if and only if the age of the data is too old +2 weeks
# using the scryfall api
# print out the file to an excel dock

# todo add gui component that makes this applet more functional
# todo load images into gui component


# todo still very slow... while this ensures it doesn't break scryfalls fair use,
#  it would be good to reduce time for these queries using threadpool

# todo I should have done proper preprocessing first, instead of doing a ton of error handling

# todo Handle Shared case.

# todo instead of having a "full collection" that we must parse, instead, concatenate everything in the sublist,
#   except for the stuff marked Shared,


# used to access string similarity
def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# queries scryfall and returns the result in a json, which in python is formatted as a dictionary
def query_scryfall_for_json(card_name):
    return requests.get(
        "https://api.scryfall.com/cards/search?q=" + card_name.replace(' ', '+') + "&unique=prints").json()


# filter card_list for correct data to append to input_data
def filter_correct_card_data(input_data, card_list, foil=False):
    if 'Set' in input_data and len(input_data['Set']) != 0:
        for card in card_list:
            if card['set'].upper() == input_data['Set'].upper().strip() \
                    and similar(card['name'], input_data['Name']) > 0.9:
                return card
        print("Your set code has a spelling error: " + input_data["Set"])
        print("defaulting to lowest price version")

    minimum = float('inf')
    curr_min = {}
    for card in card_list:
        if card['prices']['usd'] is not None and similar(card['name'], input_data['Name']) > 0.85:
            if foil:
                if card['prices']['usd_foil'] is not None:
                    if float(card['prices']['usd_foil']) < minimum:
                        minimum = float(card['prices']['usd_foil'])
                        curr_min = card
            else:
                if card['prices']['usd'] is not None:
                    if float(card['prices']['usd']) < minimum:
                        minimum = float(card['prices']['usd'])
                        curr_min = card
    return curr_min


# adds relevant data to the card in question
# THIS FUNCTION CHANGES THE DATA!
def update_card_data(card_to_update, card_data_to_add, foil=False):
    card_to_update['Set'] = card_data_to_add['set'].upper()
    if foil:
        card_to_update['Price'] = float(card_data_to_add['prices']['usd_foil'])
    else:
        card_to_update['Price'] = float(card_data_to_add['prices']['usd'])
    card_to_update['Name'] = card_data_to_add['name']
    card_to_update['last_accessed'] = date.today().strftime('%d/%m/%Y')

    # todo haven't decided whether I want to keep this data yet
    # card_to_update['Foil?'] = foil # i think it makes it look really messy
    # if card_to_update["Count"] == float("nan"):
    #     card_to_update["Count"] = 1


# todo add error handling here
def parse_true(text):
    return text.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']


# THIS FUNCTION EXPLICITLY CHANGES INPUT_DATA
def process_response_data(input_data, response_data):
    # todo should probably think about what a base file looks like, or think about what preprocessing should be
    #  done to make the code more generalized

    if 'last_accessed'in input_data:
        if len(input_data['last_accessed']) is not 0:
            try:
                last_accessed = dt.strptime(input_data['last_accessed'], "%d/%m/%Y")
                delta = date.today()-last_accessed.date()
                if delta.days < 14:
                    return
            except ValueError:  # sometimes the datestring might not be correct!
                print("there's something wrong with the date recorded in last_accessed:")
                print(input_data['last_accessed'] + " is not parsable!")

    card_data = filter_correct_card_data(input_data, response_data, parse_true(input_data['Foil?']))
    update_card_data(input_data, card_data, parse_true(input_data['Foil?']))


# very lazy implementation, I have no idea how it works
def auto_fit_col_width(filename):
    dfs = pd.read_excel(filename, sheet_name=None)
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    for sheetname, df in dfs.items():  # loop through `dict` of dataframes
        df.to_excel(writer, sheet_name=sheetname, index=False)  # send df to writer
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width
    writer.save()


def manage():
    dfs = pd.read_excel('Full collection.xlsx', sheet_name=None)
    writer = pd.ExcelWriter('Full collection.xlsx', engine='xlsxwriter')

    full_collection_list = []

    for df in dfs:
        if df == "Full Collection":
            continue

        print(dfs[df].head())

        # todo this will be an implementation of the specific case of full collection, I will make this generic in future
        input_card_df = dfs[df].fillna('')  # this converts it into list of dictionaries
        output_card_list = []

        # todo turns out is not thaat slow, a query takes around 1.40s still, there is a lot of room to optimize
        for index, row in input_card_df.iterrows():
            input_card = row.to_dict()

            print("getting... " + input_card["Name"])
            start = time.time()

            # get list of all editions from scryfall
            response_json = query_scryfall_for_json(input_card["Name"])

            if response_json['object'] == 'error':
                print("uh oh, you made a typo for card " + input_card["Name"] + ", and we can't find it!")
                print("we've left the card as is...")
                output_card_list.append(input_card)
                continue

            process_response_data(input_card, response_json["data"])

            print(input_card)

            # todo may need to cleanup, there's a lot of repeated effort here tbh.
            output_card_list.append(input_card)
            if not parse_true(input_card["Shared?"]):
                full_collection_list.append(input_card)

            print("time taken for this query is (in ms):")
            print(time.time() - start)

        pd.DataFrame(output_card_list).to_excel(writer, sheet_name=df, index=False)



    pd.DataFrame(full_collection_list).to_excel(writer, sheet_name="Full Collection", index=False)

    writer.save()

    auto_fit_col_width("Full collection.xlsx")


if __name__ == "__main__":
    manage()
