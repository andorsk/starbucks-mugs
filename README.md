# starbucks-mugs

I got tired of trying to track my starbucks mugs I collect, so I scraped
https://starbucks-mugs.com/category/been-there/ and put a little website up to
track it. 

Feel free to fork this into your own thing and just update the `owned_mugs.txt`
for changing the markers.

Thank you to starbucks-mugs.com for providing the data. Uses GoogleAPI for geocoding.

## Rules I Use For Collection 

- [ ] Must be bought at a Starbucks. i.e no ordering online. 
- [ ] Must have visited the location and outside of the airport of the location. i.e layovers don't count. 
- [ ] You MAY ask a friend, not a stranger, to pick it up for you, as long as both of you follow the previous two criteria. They must bring it to you personally. 

## Environment Variables

|                         |                                                    |
|-------------------------|----------------------------------------------------|
| **GOOGLE_MAPS_API_KEY** | Set to Google Maps API Key. Required for GeoCoding |

## Usage

1. `python -m pip install -r requirements.txt`: Download reqs
2. `python starbucks-mugs.py update` to update the data.


