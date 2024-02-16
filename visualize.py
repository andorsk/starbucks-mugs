#!/usr/bin/env python3
import json
import folium
import base64

def modify_and_encode_svg(svg_path, new_color):
    with open(svg_path, 'r') as file:
        svg_content = file.read()
    encoded_svg = svg_content
    modified_svg_content = encoded_svg.replace('#000000', f'{new_color}')
    svg_base64 =  base64.b64encode(modified_svg_content.encode('utf-8')).decode()
    data_uri = f"data:image/svg+xml;base64,{svg_base64}"
    return data_uri

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
    c = 'green' if d['owned'] is True else 'orange'
    icon_image = modify_and_encode_svg('./icon.svg', c)
    icon = folium.CustomIcon(icon_image, icon_size=(30, 30))  # Adjust size as needed
    folium.Marker(
        location=d["latlong"],
        popup=popup,
        icon=icon,
        fill_opacity=0.6,
        tooltip=tooltip
    ).add_to(m)

m.save('index.html')
