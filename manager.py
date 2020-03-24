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


def main():
    today = date.today()
    fdate = date.today().strftime('%d/%m/%Y')
    print('the date is: ' + fdate)

    dfs = pd.read_excel('Full collection.xlsx', sheet_name=None)
    for df in dfs:
        print(dfs[df].head())

    output_dict = []
    for index, row in dfs["FULL COLLECTION"].iterrows():
        print("getting... " + row["Name"])
        start = time.time()

        # get list of all editions from scryfall
        response = requests.get("https://api.scryfall.com/cards/search?q=" + row["Name"].replace(' ', '+') + "&unique=prints").json()

        if len(response["data"]) == 0:
            print("uh oh, you made a typo for card " + row["Name"] + ", and we can't find it!")
            continue

        # we care about name, set, set_name, price, date we accessed.
        output_dict.append({})

        end = time.time()
        print("time taken for this query is (in ms):")
        print(end - start)



if __name__ == "__main__":
    main()