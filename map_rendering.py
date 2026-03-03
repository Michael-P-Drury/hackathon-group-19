import math
import osmnx as ox
import networkx as nx
import folium
import webbrowser
from shapely.geometry import Point
import asyncio



async def render_map():

    user_hazards = []

    with open("user_reports.txt", "r") as file:
        for line in file:
            line_list = line.split('|')

            user_hazards.append((line_list[0], line_list[1], line_list[2], float(line_list[3]), line_list[4]))

    # bit of set up
    center_point = (51.4820, -3.1750) 
    G = ox.graph_from_point(center_point, dist=1000, network_type='walk')

    # hazards array - could be from user input or IoT sensor
    sensor_hazards = [
        (51.4835, -3.1760, "noise", 9, "Sensor input"),
        (51.4845, -3.1790, "noise", 4, "Sensor input"),
        (51.4825, -3.1730, "vision", 8, "Sensor input"),
        (51.4792, -3.1775, "vision", 5, "Sensor input")
    ]
    danger_radius = 0.0015

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

        data['accessible_weight'] = data['length'] * max_penalty

    # start end coords
    start_coords = (51.4820, -3.1750) 
    end_coords = (51.4855, -3.1775)
    origin_node = ox.distance.nearest_nodes(G, X=start_coords[1], Y=start_coords[0])
    target_node = ox.distance.nearest_nodes(G, X=end_coords[1], Y=end_coords[0])

    # 
    # fastest path (not accessible)
    standard_route = nx.shortest_path(G, origin_node, target_node, weight='length')

    # Accessible Route (Avoids the hazards (hopefully))
    accessible_route = nx.shortest_path(G, origin_node, target_node, weight='accessible_weight')

    # generate
    route_map = folium.Map(location=center_point, zoom_start=15)

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


asyncio.run(render_map())