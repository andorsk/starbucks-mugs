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

owned_count = 0
total_count = len(data.keys())

for c, d in data.items():
    tooltip = c
    if d.get('owned') is True:
        owned_count += 1

    if 'latlong' not in d:
        continue

    imgPath = d.get('img', "")
    url = d.get('url', "")
    description = d.get('description', "")

    markerData = f'<img src="{imgPath}" width="200"><br><a href="{url}">Link</a><br>{description}'
    iframe = folium.IFrame(markerData, width=250, height=300)
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

header_html = f"<div style='position: fixed; top: 10px; left: 50px; width: 300px; height: 20px; background-color: white; z-index:9999; font-size:16px;'><b>Owned: {owned_count} / Total: {total_count}</b></div>"
m.get_root().html.add_child(folium.Element(header_html))
m.save('index.html')
