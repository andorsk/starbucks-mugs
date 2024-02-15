#!/usr/bin/env python3
import json
import folium

# Initialize a map centered around Charlotte
f = open('final_data.json', 'r')
data = json.load(f)

# Initialize a map centered around the first city in the list
m = folium.Map(location=data[list(data.keys())[0]]["latlong"], zoom_start=4)

# Iterate over each city in the data list
for c, d in data.items():
    tooltip = c
    if 'img' not in d or 'url' not in d or 'description' not in d or 'latlong' not in d:
        continue
    description = f'<img src="{d["img"]}" width="200"><br><a href="{d["url"]}">Link</a><br>{d["description"]}'
    iframe = folium.IFrame(description, width=250, height=300)
    popup = folium.Popup(iframe, max_width=300)
    c = 'green' if d['owned'] is True else 'yellow'
    folium.Marker(
        location=d["latlong"],
        popup=popup,
        icon=folium.Icon(color=c),  # This sets the marker color to black
        fill_opacity=0.6,
        tooltip=tooltip
    ).add_to(m)

m.save('map.html')
