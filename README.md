# Collection Manager

I, like many mtg players have a completely unmanageable collection, and I hate the idea of paying a subscriber fee to echo mtg.

So instead of paying like 3 dollars a month to manage my collection, I decided to spend 10+ hours writing this collection manager app in python.

This project makes use of the scryfall api to slowly populate the data fields in your collection. It's not really suitable to *HUGE* collections, because at 10 queries a second, it's still going to take hours to go through truly huge ones.

Collections with 100k cards will take an hour and 40 minutes to run, for instance.

I might write this in clojure too, who knows.