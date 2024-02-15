#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import geocoder
import json
import time
import os

API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

def fetch_complete_list():
    pages = 33
    all_titles = []
    base_url = 'https://starbucks-mugs.com/category/been-there/'
    for page in range(1, pages + 1):
        url = base_url if page == 1 else f'{base_url}page/{page}/'
        titles = fetch_url(url)
        all_titles.extend(titles)
    return all_titles

def fetch_url(url):
    titles = []
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception("Failed to fetch page")
    soup = BeautifulSoup(resp.text, 'html.parser')
    for entry in soup.find_all(class_='mug'):
        title = entry.find_all(class_='entry-title')
        imgs = entry.find_all('img')
        ee = entry.find_all(class_='entry')
        if title is None or len(title) == 0:
            print("skip entry without title", entry)
            continue
        row = {
            'title': title[0].text,
            'url': entry.find('a')['href'],
            'img': imgs[0]['src'],
            'description': ee[0].text
        }
        titles.append(row)
    return titles

def read_owned():
    with open('./owned_mugs.txt', 'r') as file:
        owned = file.readlines()
    return [line.strip() for line in owned]

def get_latlong(address, api_key='AIzaSyAAyy05twpmpK7NAhxrIdWYtQQ50ijbBag'):
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    endpoint = f"{base_url}address={address}&key={api_key}"
    params = {'sensor': 'false', 'address': address, 'key': api_key}
    resp = requests.get(base_url, params=params)
    if resp.status_code != 200:
        print(f"Failed to fetch latlong for {address}. Status code: {resp.status_code}")
        raise Exception(f"Failed to fetch latlong for {address}. Status code: {resp.status_code}")
    data = resp.json()
    if data['status'] != 'OK':
        print(f"Failed to fetch latlong for {address}. Status: {data['status']}")
        raise Exception(f"Failed to fetch latlong for {address}. Status: {data['status']}")
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']
    time.sleep(1) # for rate limiting
    return [lat, lng]

def prepare():
    owned_mugs = read_owned()
    all_titles = fetch_complete_list()
    data = {}
    for title in all_titles:
        data[title['title']] = {
            'owned': title['title'] in owned_mugs,
            **title
        }
    for m in owned_mugs:
        if m not in data:
            data[m] = {
                'owned': True
            }

    updated = {}
    # clean keys
    for k, v in data.items():
        print(k)
        try:
            new_key = k.split("–")[1]
            new_key = new_key.strip()
            updated[new_key] = v
        except Exception as e:
            print("Failed to clean key", k)
            print(e)

    data = updated
    # get addresses
    for k in data.keys():
        try:
            data[k]['latlong'] = get_latlong(k)
        except Exception as e:
            print(f"Failed to get latlong for {k}")
            print(e)

    with open('final_data.json', 'w') as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    prepare()
