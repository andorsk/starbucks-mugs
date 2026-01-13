#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import geocoder
import json
import time
import os
import json
import folium
import base64
import argparse
import copy

GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

def modify_and_encode_svg(svg_path, new_color):
    with open(svg_path, 'r') as file:
        svg_content = file.read()
    encoded_svg = svg_content
    modified_svg_content = encoded_svg.replace('#000000', f'{new_color}')
    svg_base64 =  base64.b64encode(modified_svg_content.encode('utf-8')).decode()
    data_uri = f"data:image/svg+xml;base64,{svg_base64}"
    return data_uri

def visualize(data_path, output_path="index.html"):
    f = open(data_path, 'r')
    data = json.load(f)
    m = folium.Map(location=[34.0549076, -118.242643], zoom_start=4, tiles=None)

    # Add multiple tile layers
    folium.TileLayer('OpenStreetMap', name='Standard').add_to(m)
    folium.TileLayer('CartoDB positron', name='Light').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Dark').add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite'
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Terrain'
    ).add_to(m)
    owned_count = 0
    total_count = len(data.keys())
    print("got total count", total_count)
    for c, d in data.items():
        tooltip = c
        if d.get('owned') is True:
            owned_count += 1
        if 'latlong' not in d:
            print("can't find latlong")
            continue

        imgPath = d.get('img', "")
        url = d.get('url', "")
        description = d.get('description', "")
        markerData = f'<img src="{imgPath}" width="200"><br><a href="{url}">Link</a><br>{description}'
        iframe = folium.IFrame(markerData, width=250, height=300)
        popup = folium.Popup(iframe, max_width=300)
        color = 'green' if d['owned'] is True else 'orange'
        icon_image = modify_and_encode_svg('./assets/icon.svg', color)
        icon = folium.CustomIcon(icon_image, icon_size=(30, 30))  # Adjust size as needed
        folium.Marker(
                location=d["latlong"],
                popup=popup,
                icon=icon,
                fill_opacity=0.6,
                tooltip=tooltip
        ).add_to(m)

    # Add layer control
    folium.LayerControl(position='topleft').add_to(m)

    footer_html = f"<div style='position: fixed; bottom: 10px; left: 10px; height: 20px; background-color: white; z-index:9999; font-size:14px; padding: 2px 8px; border-radius: 4px;'>Credit to <a href='https://starbucks-mugs.com/category/been-there/'>starbucks-mugs.com</a> | <a href='https://github.com/andorsk/starbucks-mugs.git'>Github</a></div>"
    
    header_html = f"""<div style='position: fixed; top: 10px; left: 50%; transform: translateX(-50%); background: white; z-index: 999; padding: 10px 20px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.15); font-family: -apple-system, BlinkMacSystemFont, sans-serif; display: flex; align-items: center; gap: 20px;'>
        <span style='font-size: 15px; color: #1e3932;'><strong style='color: #00704A;'>{owned_count}</strong> owned of <strong>{total_count}</strong> mugs</span>
        <span style='font-size: 13px; color: #666; display: flex; align-items: center; gap: 12px;'>
            <span style='display: flex; align-items: center; gap: 4px;'><svg height='10' width='10'><circle cx='5' cy='5' r='5' fill='#00704A'/></svg> Owned</span>
            <span style='display: flex; align-items: center; gap: 4px;'><svg height='10' width='10'><circle cx='5' cy='5' r='5' fill='#f58220'/></svg> Not Owned</span>
        </span>
    </div>"""

    # Build mug list panel
    sorted_mugs = sorted(data.items(), key=lambda x: (not x[1].get('owned', False), x[0]))
    mug_items = []
    mug_data_js = []
    for name, info in sorted_mugs:
        owned = info.get('owned', False)
        icon = '&#x2705;' if owned else '&#x25CB;'
        color = '#2d5016' if owned else '#666'
        owned_class = 'owned' if owned else 'not-owned'
        latlong = info.get('latlong', [0, 0])
        img = info.get('img', '')
        url = info.get('url', '')
        desc = info.get('description', '').replace("'", "\\'").replace("\n", " ")[:200]
        safe_name = name.replace("'", "\\'")
        mug_items.append(f"<div class='mug-item {owned_class}' data-name='{safe_name}' style='padding: 8px 12px; border-bottom: 1px solid #eee; color: {color}; cursor: pointer;' onclick=\"showMug('{safe_name}')\">{icon} {name}</div>")
        if latlong and latlong[0] != 0:
            mug_data_js.append(f"'{safe_name}': {{lat: {latlong[0]}, lng: {latlong[1]}, img: '{img}', url: '{url}', desc: '{desc}', owned: {str(owned).lower()}}}")

    panel_html = f"""
    <style>
        .mug-item:hover {{ background: #f0f0f0; }}
        .filter-btn {{ padding: 6px 12px; border: 1px solid #ddd; background: white; cursor: pointer; font-size: 12px; }}
        .filter-btn.active {{ background: #00704A; color: white; border-color: #00704A; }}
        #mug-modal, #info-modal {{ display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 0; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); z-index: 10001; max-width: 350px; width: 90%; }}
        #info-modal {{ max-width: 450px; }}
        #info-btn {{ position: fixed; bottom: 40px; left: 10px; z-index: 10000; background: #1e3932; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        #modal-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000; }}
        #mug-panel {{ transition: transform 0.3s ease; }}
        #mug-panel.collapsed {{ transform: translateX(280px); }}
        #panel-toggle {{ position: fixed; top: 10px; right: 290px; z-index: 10000; background: #00704A; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: right 0.3s ease; }}
        #panel-toggle.collapsed {{ right: 10px; }}
    </style>
    <button id='info-btn' onclick='showInfo()'>&#x2139; Info</button>
    <button id='panel-toggle' onclick='togglePanel()'>&#x2630; Mugs</button>
    <div id='modal-overlay' onclick='closeModal()'></div>
    <div id='info-modal'>
        <div style='padding: 12px 16px; background: #00704A; color: white; font-weight: bold; border-radius: 8px 8px 0 0;'>
            <span>starbucks-mugs</span>
            <span onclick='closeModal()' style='float: right; cursor: pointer; font-size: 18px;'>&times;</span>
        </div>
        <div style='padding: 16px; font-size: 14px; line-height: 1.6;'>
            <p style='margin: 0 0 12px 0;'>I got tired of trying to track my Starbucks mugs I collect, so I scraped <a href='https://starbucks-mugs.com/category/been-there/' target='_blank'>starbucks-mugs.com</a> and put a little website up to track it.</p>
            <p style='margin: 0 0 12px 0;'>Feel free to fork this into your own thing and just update the <code>owned_mugs.txt</code> for changing the markers.</p>
            <p style='margin: 0 0 12px 0; font-size: 12px; color: #666;'>Thank you to starbucks-mugs.com for providing the data. Uses Google API for geocoding.</p>
            <div style='background: #f5f5f5; padding: 12px; border-radius: 4px; margin-bottom: 12px;'>
                <strong style='color: #00704A;'>Rules I Use For Collection</strong>
                <ul style='margin: 8px 0 0 0; padding-left: 20px;'>
                    <li>Must be bought at a Starbucks. i.e. no ordering online.</li>
                    <li>Must have visited the location and outside of the airport. i.e. layovers don't count.</li>
                    <li>You MAY ask a friend, not a stranger, to pick it up for you, as long as both of you follow the previous two criteria. They must bring it to you personally.</li>
                </ul>
                <p style='margin: 8px 0 0 0; font-size: 12px; color: #666; font-style: italic;'>Note: This has become a family thing, so I have extended some leniency to my immediate family on the rules.</p>
            </div>
            <a href='https://github.com/andorsk/starbucks-mugs' target='_blank' style='display: block; padding: 10px; background: #1e3932; color: white; text-align: center; border-radius: 4px; text-decoration: none;'>Clone on GitHub</a>
        </div>
    </div>
    <div id='mug-modal'>
        <div style='padding: 12px 16px; background: #00704A; color: white; font-weight: bold; border-radius: 8px 8px 0 0;'>
            <span id='modal-title'>Mug Name</span>
            <span onclick='closeModal()' style='float: right; cursor: pointer; font-size: 18px;'>&times;</span>
        </div>
        <div style='padding: 16px;'>
            <img id='modal-img' src='' style='width: 100%; max-height: 200px; object-fit: contain; margin-bottom: 12px;'>
            <p id='modal-desc' style='font-size: 14px; color: #666; margin: 0 0 12px 0;'></p>
            <div style='display: flex; gap: 8px;'>
                <button onclick='viewOnMap()' style='flex: 1; padding: 10px; background: #00704A; color: white; border: none; border-radius: 4px; cursor: pointer;'>View on Map</button>
                <a id='modal-link' href='' target='_blank' style='flex: 1; padding: 10px; background: #1e3932; color: white; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; text-align: center;'>More Info</a>
            </div>
        </div>
    </div>
    <div id='mug-panel' style='position: fixed; top: 0; right: 0; width: 280px; height: 100vh; background: white; z-index: 9999; box-shadow: -2px 0 8px rgba(0,0,0,0.15); display: flex; flex-direction: column;'>
        <div style='padding: 12px; background: #00704A; color: white; font-weight: bold; font-size: 16px;'>
            Mug Collection ({owned_count}/{total_count})
        </div>
        <input type='text' id='mug-search' placeholder='Search mugs...' style='margin: 8px 8px 4px 8px; padding: 8px; border: 1px solid #ddd; border-radius: 4px;' onkeyup='filterMugs()'>
        <div style='display: flex; margin: 4px 8px 8px 8px; gap: 4px;'>
            <button class='filter-btn active' onclick='setFilter("all")'>All</button>
            <button class='filter-btn' onclick='setFilter("owned")'>Owned</button>
            <button class='filter-btn' onclick='setFilter("not-owned")'>Not Owned</button>
        </div>
        <div id='mug-list' style='flex: 1; overflow-y: auto; font-size: 14px;'>
            {''.join(mug_items)}
        </div>
        <div style='padding: 8px; background: #f5f5f5; font-size: 12px; text-align: center;'>
            &#x2705; = Owned &nbsp; &#x25CB; = Not Owned
        </div>
    </div>
    <script>
    var mugData = {{{', '.join(mug_data_js)}}};
    var currentMug = null;
    var currentFilter = 'all';

    function filterMugs() {{
        var input = document.getElementById('mug-search').value.toLowerCase();
        var items = document.querySelectorAll('.mug-item');
        items.forEach(function(item) {{
            var text = item.textContent.toLowerCase();
            var matchesSearch = text.includes(input);
            var matchesFilter = currentFilter === 'all' || item.classList.contains(currentFilter);
            item.style.display = (matchesSearch && matchesFilter) ? '' : 'none';
        }});
    }}

    function setFilter(filter) {{
        currentFilter = filter;
        document.querySelectorAll('.filter-btn').forEach(function(btn) {{
            btn.classList.remove('active');
        }});
        event.target.classList.add('active');
        filterMugs();
    }}

    function showMug(name) {{
        currentMug = name;
        var mug = mugData[name];
        document.getElementById('modal-title').textContent = name;
        if (mug) {{
            document.getElementById('modal-img').src = mug.img || '';
            document.getElementById('modal-img').style.display = mug.img ? '' : 'none';
            document.getElementById('modal-desc').textContent = mug.desc || '';
            document.getElementById('modal-link').href = mug.url || '#';
        }}
        document.getElementById('modal-overlay').style.display = 'block';
        document.getElementById('mug-modal').style.display = 'block';
    }}

    function closeModal() {{
        document.getElementById('modal-overlay').style.display = 'none';
        document.getElementById('mug-modal').style.display = 'none';
        document.getElementById('info-modal').style.display = 'none';
    }}

    function viewOnMap() {{
        var mug = mugData[currentMug];
        if (mug && mug.lat) {{
            var mapObj = Object.values(window).find(v => v && v._leaflet_id && v.setView);
            if (mapObj) {{
                mapObj.setView([mug.lat, mug.lng], 10);
            }}
        }}
        closeModal();
    }}

    function togglePanel() {{
        var panel = document.getElementById('mug-panel');
        var toggle = document.getElementById('panel-toggle');
        panel.classList.toggle('collapsed');
        toggle.classList.toggle('collapsed');
        if (panel.classList.contains('collapsed')) {{
            toggle.innerHTML = '&#x2630; Mugs';
        }} else {{
            toggle.innerHTML = '&times; Hide';
        }}
    }}

    function showInfo() {{
        document.getElementById('modal-overlay').style.display = 'block';
        document.getElementById('info-modal').style.display = 'block';
    }}
    </script>
    """

    m.get_root().html.add_child(folium.Element(header_html))
    m.get_root().html.add_child(folium.Element(footer_html))
    m.get_root().html.add_child(folium.Element(panel_html))

    m.save(output_path)

def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def update(new, old):
    ret = {}

    for key, oldEntry in old.items():
        newEntry = new.get(key)
        if newEntry is None:
            ret[key] = oldEntry
            continue

    for key, newEntry in new.items():
        oldEntry = old.get(key)
        ret[key] = newEntry # add new values

    return ret

def modify_and_encode_svg(svg_path, new_color):
    with open(svg_path, 'r') as file:
        svg_content = file.read()
    encoded_svg = svg_content
    modified_svg_content = encoded_svg.replace('#000000', f'{new_color}')
    svg_base64 =  base64.b64encode(modified_svg_content.encode('utf-8')).decode()
    data_uri = f"data:image/svg+xml;base64,{svg_base64}"
    return data_uri


def fetch_complete_list():
    pages = 36
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
    with open('./data/owned_mugs.txt', 'r') as file:
        owned = file.readlines()
    return [line.strip() for line in owned]

def read_latlong_overrides():
    with open('./data/latlong_overrides.json', 'r') as file:
        overrides = json.load(file)
        return overrides

def get_latlong(address, api_key=''):
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    endpoint = f"{base_url}address={address}&key={api_key}"
    print("trying to fetch latlong for", endpoint)
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

def prepare(previous_data_path, output_file_path):

    owned_mugs = read_owned()
    latlong_overrides = read_latlong_overrides()
    all_titles = fetch_complete_list()
    data = {}
    previous_data = {}

    if previous_data_path:
        previous_data = read_json(previous_data_path)
        data = copy.deepcopy(previous_data)

    def insert_owned_mugs(data):
        # update the titles of ownership
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
        return data

    def clean_keys(data):
        updated = {}
        for k, v in data.items():
            print(k)
            try:
                new_key = k.split("–")[1]
                new_key = new_key.strip()
                updated[new_key] = v
            except Exception as e:
                print("Failed to clean key", k)
                print(e)
        return updated

    def get_addresses(data):
        for k in data.keys():
            try:
                if k in latlong_overrides:
                    data[k]['latlong'] = latlong_overrides[k]
                    print("using override for", k)
                else:
                    data[k]['latlong'] = get_latlong(k, GOOGLE_MAPS_API_KEY)
            except Exception as e:
                print(f"Failed to get latlong for {k}")
                print(e)
        return data

    data = insert_owned_mugs(data)
    data = clean_keys(data)
    data = get_addresses(data)
    data = update(previous_data, data)
    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def backup(input_file, output_file):
    data = read_json(input_file)
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for data manipulation tasks")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup old file")
    backup_parser.add_argument("--input", default="final_data.json", help="Input file (default: final_data.json)")
    backup_parser.add_argument("--output", default="old_data.json", help="Output file (default: old_data.json)")

    # Prepare command
    prepare_parser = subparsers.add_parser("prepare", help="Prepare data")
    prepare_parser.add_argument("--output", required=True, help="Output file")
    prepare_parser.add_argument("--previous", required=False, help="Previous Data File", default="final_data.json")

    # Visualize command
    visualize_parser = subparsers.add_parser("visualize", help="Visualize data")
    visualize_parser.add_argument("--input", default="final_data.json", help="Input file (default: final_data.json)")
    visualize_parser.add_argument("--output", default="index.html", help="Output file (default: index.html)")

    update_parser = subparsers.add_parser("update", help="update data")
    update_parser.add_argument("--backup_path", default="data/final_data.json.bak", help="backup file")
    update_parser.add_argument("--output", required=False, help="Output file", default="index.html")
    update_parser.add_argument("--previous", required=False, help="Previous Data File", default="data/final_data.json")
    args = parser.parse_args()

    if args.command == "backup":
        backup(args.input, args.output)
    elif args.command == "prepare":
        prepare(args.previous, args.output)
    elif args.command == "visualize":
        visualize(args.input, args.output)
    elif args.command == "update":
        # backup old data with .bak
        backup(args.previous, args.backup_path)
        # preapare new file. overwriting the new one
        prepare(args.previous, args.previous)
        # create the html
        visualize(args.previous, args.output)
