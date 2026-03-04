import math
import osmnx as ox
import networkx as nx
import folium
import webbrowser
from shapely.geometry import Point
import asyncio
from get_location import get_coordinates



async def render_map(destination, persona):

    visual_concern = persona[0]

    noise_concern = persona[1]

    destination_coords = await get_coordinates(destination)

    destination_latitude = destination_coords["latitude"]
    destination_longitude = destination_coords["longitude"]

    input_user_hazards = []

    with open("user_reports.txt", "r") as file:
        for line in file:
            line_list = line.split('|')

            input_user_hazards.append((line_list[0], line_list[1], line_list[2], float(line_list[3]), line_list[4]))

    user_hazards = []

    for hazard in input_user_hazards:
        current_hazard_noise = False

        if hazard[2] == 'noise':
            current_hazard_noise = True
        
        if visual_concern:
            if not current_hazard_noise:
                user_hazards.append(hazard)
        
        if noise_concern:
            if current_hazard_noise:
                user_hazards.append(hazard)

    # bit of set up
    center_point = (51.4820, -3.1750) 
    G = ox.graph_from_point(center_point, dist=3000, network_type='walk')

    map_hazards = [
        ('highways', 'noise',  'primary', 3),
        ('railways', 'noise',  '*',       2),
        ('shop',     'vision', '*',       1)
    ]

    # hazards array - could be from user input or IoT sensor
    input_sensor_hazards = [
        (51.4835, -3.1760, "noise", 9, "Sensor input"),
        (51.4845, -3.1790, "noise", 4, "Sensor input"),
        (51.4825, -3.1730, "vision", 8, "Sensor input"),
        (51.4792, -3.1775, "vision", 5, "Sensor input")
    ]
    danger_radius = 0.0015

    sensor_hazards = []

    for hazard in input_sensor_hazards:
        current_hazard_noise = False

        if hazard[2] == 'noise':
            current_hazard_noise = True
        
        if visual_concern:
            if not current_hazard_noise:
                sensor_hazards.append(hazard)
        
        if noise_concern:
            if current_hazard_noise:
                sensor_hazards.append(hazard)

    
    for u, v, k, data in G.edges(data=True, keys=True):
        node_coords = G.nodes[u]
        edge_point = Point(node_coords['x'], node_coords['y'])

        max_penalty = 1
        for h_lat, h_lon, cat, score, desc in sensor_hazards:
            h_point = Point(h_lon, h_lat)
            if edge_point.distance(h_point) < danger_radius:
                current_penalty = math.pow(2, score)
                if current_penalty > max_penalty:
                    max_penalty = current_penalty

        for h_lat, h_lon, cat, score, desc in user_hazards:
            h_point = Point(h_lon, h_lat)
            if edge_point.distance(h_point) < danger_radius:
                current_penalty = math.pow(2, score)
                if current_penalty > max_penalty:
                    max_penalty = current_penalty

        map_hazard_penalty = 0
        for hazard, cat, query, score in map_hazards:
            if data.get(hazard, query):
                map_hazard_penalty += score

        map_hazard_penalty = math.pow(2, map_hazard_penalty)/len(map_hazards)
        if max_penalty < map_hazard_penalty:
            max_penalty = map_hazard_penalty

        data['accessible_weight'] = data['length'] * max_penalty

    # start end coords
    start_coords = (51.4820, -3.1750) 
    end_coords = (destination_latitude, destination_longitude)
    origin_node = ox.distance.nearest_nodes(G, X=start_coords[1], Y=start_coords[0])
    target_node = ox.distance.nearest_nodes(G, X=end_coords[1], Y=end_coords[0])

    # 
    # fastest path (not accessible)
    standard_route = nx.shortest_path(G, origin_node, target_node, weight='length')

    # Accessible Route (Avoids the hazards (hopefully))
    accessible_route = nx.shortest_path(G, origin_node, target_node, weight='accessible_weight')

    # generate
    route_map = folium.Map(location=center_point, zoom_start=15, tiles="CartoDB positron")

    # Convert routes to coordinates
    std_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in standard_route]
    acc_coords = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in accessible_route]

    # draw both routes
    # Standard route in RED 
    folium.PolyLine(std_coords, color='red', weight=4, opacity=0.6, 
                    dash_array='10', popup="Standard Route (Noisy)").add_to(route_map)

    # Accessible route in GREEN
    folium.PolyLine(acc_coords, color='#2e7d32', weight=7, opacity=0.9, 
                    popup="Accessible Route (Quiet)").add_to(route_map)

    # visual stuff
    for h_lat, h_lon, cat, score, desc in sensor_hazards:
        if cat == "noise":
            icon_type = "volume-up"
            circ_color = "red"
        else:
            icon_type = "eye-slash"
            circ_color = "orange"

        folium.Circle(
            location=[h_lat, h_lon],
            radius=60 + (score * 4),
            color=circ_color,
            fill=True,
            fill_opacity=score/20,
            popup=f"<b>{cat.upper()}</b><br>Score: {score}/10<br><i>{desc}</i>"
        ).add_to(route_map)

        folium.Marker(
            location=[h_lat, h_lon],
            icon=folium.Icon(color=circ_color, icon=icon_type, prefix='fa'),
            tooltip=cat.capitalize()
        ).add_to(route_map)

    for h_lat, h_lon, cat, score, desc in user_hazards:
        if cat == "noise":
            icon_type = "volume-up"
            circ_color = "red"
        else:
            icon_type = "eye-slash"
            circ_color = "orange"

        folium.Circle(
            location=[h_lat, h_lon],
            radius=60 + (score * 4),
            color=circ_color,
            fill=True,
            fill_opacity=score/20,
            popup=f"<b>{cat.upper()}</b><br>Score: {score}/10<br><i>{desc}</i>"
        ).add_to(route_map)

        folium.Marker(
            location=[h_lat, h_lon],
            icon=folium.Icon(color=circ_color, icon=icon_type, prefix='fa'),
            tooltip=cat.capitalize()
        ).add_to(route_map)

    folium.Marker(location=start_coords, popup="Start", icon=folium.Icon(color='blue')).add_to(route_map)
    folium.Marker(location=end_coords, popup="Destination", icon=folium.Icon(color='black')).add_to(route_map)

    #  legend
    legend_html = '''
        <div style="position: fixed; bottom: 50px; left: 50px; width: 180px; height: 90px; 
        border:2px solid grey; z-index:9999; font-size:14px; background-color:white;
        padding: 10px;">
        <b>Route Comparison</b><br>
        <i style="color:red;">---</i> Standard Route<br>
        <i style="color:green;">&mdash;</i> Accessible Route
        </div>
        '''
    route_map.get_root().html.add_child(folium.Element(legend_html))

    #  Save and Open
    output_file = "cardiff_comparison_map.html"
    route_map.save(output_file)
    webbrowser.open(output_file)


asyncio.run(render_map('150 Woodville Road', [False, True]))