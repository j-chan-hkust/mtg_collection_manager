import os
import pandas as pd
import requests
import time
from datetime import date

# walk through the file list in "new additions" directory
# load the existing inventory list from the generated excel
# combine existing inventory with new additions
# fill in auxiliary data, if and only if the age of the data is too old +2 weeks
# using the scryfall api
# print out the file to an excel dock

#todo add check for foiling
#todo add check for
#todo handle formatting issues when writing to excel
#todo if completely rewrites the excel file, need to fix that
#todo convert price text to number
#todo shorter names will get the wrong similar longer names, e.g. berserk -> vulshok berserker
#todo weird bug where sol ring and birds of paradise is picking up the foreign black border version




def main():
    today = date.today()
    fdate = date.today().strftime('%d/%m/%Y')
    print('the date is: ' + fdate)

    dfs = pd.read_excel('Full collection.xlsx', sheet_name=None)
    for df in dfs:
        print(dfs[df].head())

    # todo this will be an implementation of the specific case of full collection, I will make this generic in future

    input_dict = dfs["FULL COLLECTION"].fillna('').to_dict('records') #this converts it into list of dictionaries

    output_dicts = []

    for dict_entry in input_dict:
        print("getting... " + dict_entry["Name"])
        start = time.time()

        # get list of all editions from scryfall
        response = requests.get("https://api.scryfall.com/cards/search?q=" + dict_entry["Name"].replace(' ', '+') + "&unique=prints").json()

        if response['object'] == 'error':
            print("uh oh, you made a typo for card " + dict_entry["Name"] + ", and we can't find it!")
            output_dicts.append(dict_entry)
            continue

        response_data = response['data']

        # we care about name, set, set_name, price, date we accessed.

        # this section here helps us to extract the appropriate printing
        card_data = {} #this stores the card data that matches the version we want
        if 'Set' in dict_entry and len(dict_entry['Set']) != 0:
            for dict in response_data:
                if dict['set'].upper() == dict_entry['Set'].upper().strip():
                    card_data = dict
                    break
        else:
            min = float('inf')
            for dict in response_data:
                if dict['prices']['usd'] is not None:
                    if float(dict['prices']['usd']) < min:
                        card_data = dict

        dict_entry['Set'] = card_data['set'].upper()
        dict_entry['Price'] = card_data['prices']['usd']
        dict_entry['Name'] = card_data['name']
        dict_entry['last_accessed'] = fdate

        print(dict_entry)

        output_dicts.append(dict_entry)

        print("time taken for this query is (in ms):")
        print(time.time() - start)


    pd.DataFrame(output_dicts).to_excel("Full collection.xlsx", sheet_name="FULL COLLECTION")



if __name__ == "__main__":
    main()