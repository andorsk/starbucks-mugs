# starbucks-mugs

I got tired of trying to track my starbucks mugs I collect, so I scraped
https://starbucks-mugs.com/category/been-there/ and put a little website up to
track it. 

Feel free to fork this into your own thing and just update the `owned_mugs.txt`
for changing the markers.

Thank you to starbucks-mugs.com for providing the data. Uses GoogleAPI for geocoding.

## Environment Variables

|                         |                                                    |
|-------------------------|----------------------------------------------------|
| **GOOGLE_MAPS_API_KEY** | Set to Google Maps API Key. Required for GeoCoding |

## Usage

1. `prepare.py`: to get the encoded data and prepare the final_data.json file
2. `visualize.py`: to generate the map


# TODO

- [ ] Automatically scrape and clean the data so it runs every day. Add it to Github Actions.

