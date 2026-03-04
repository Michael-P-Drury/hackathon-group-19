import flet as ft
import flet_webview as fwv
import asyncio
import genai_call
import map_rendering_2
import urllib.parse
import os
import threading
import http.server
import socketserver
import functools

# --- TOP OF run.py ---
import os

# This gets the folder WHERE RUN.PY LIVES
#base_path = os.path.dirname(os.path.abspath(__file__))
#absolute_assets_path = os.path.join(base_path, "assets")

# Create the folder if it doesn't exist
#if not os.path.exists(absolute_assets_path):
#    os.makedirs(absolute_assets_path)

#print(f"DEBUG: Map Server is looking in: {absolute_assets_path}")

#def start_map_server():
#    try:
#        Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=absolute_assets_path)
#        socketserver.TCPServer.allow_reuse_address = True
#        httpd = socketserver.TCPServer(("0.0.0.0", 8000), Handler)
#        httpd.serve_forever()
#    except Exception as e:
#        print(f"Server error: {e}")

#threading.Thread(target=start_map_server, daemon=True).start()


async def main(page: ft.Page):
    page.title = "AccessRoute - Hackathon Group 19"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    
    # --- UI Elements ---

    report_input = ft.TextField(
        label="What is the issue?", 
        hint_text="e.g. Construction site with loud drilling", 
        multiline=True
    )
    location_input = ft.TextField(
        label="Hazard Location", 
        hint_text="e.g. Queen Street, Cardiff"
    )
    
    dest_input = ft.TextField(
        label="Where are you going?", 
        hint_text="e.g. Cardiff Central Station", 
        value="Cardiff Castle"
    )
    
    status_text = ft.Text(value="", color="blue", weight=ft.FontWeight.W_500)
    loading_ring = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2)

    # Initialize the WebView container. 
    # visible=False so it hides until the map is generated.
    # height=500 ensures it doesn't collapse inside the scrollable column.
    map_view = fwv.WebView(height=600, visible=False)

    async def submit_report(e):
        if not report_input.value or not location_input.value:
            status_text.value = "Please fill in both hazard fields!"
            page.update()
            return

        loading_ring.visible = True
        status_text.value = "Analyzing hazard with Cerebras AI..."
        page.update()

        success = await genai_call.create_report(report_input.value, location_input.value)
        
        loading_ring.visible = False
        if success:
            status_text.value = "Hazard report saved successfully!"
            report_input.value = ""
            location_input.value = ""
        else:
            status_text.value = "Error processing report. Check API Key/Connection."
        
        page.update()

    #async def open_map(e):
    #    if not dest_input.value:
    #        status_text.value = "Please enter a destination first!"
    #        page.update()
    #        return

    #    status_text.value = f"Calculating accessible route to {dest_input.value}..."
    #    page.update()
        
        # This now receives the filename (e.g., "route_12345.html")
    #    filename = await map_rendering_2.render_map(dest_input.value, [False, True])
        
    #    if filename:
            # CHANGED: Use the magic Android Emulator IP so the phone finds your laptop!
    #        map_view.url = f"http://10.0.2.2:8550/{filename}"
            
    #        map_view.visible = True
    #        status_text.value = f"Map rendered below! Route shown to {dest_input.value}."
    #    else:
    #        status_text.value = "Error generating map."
            
    #    page.update()

    async def open_map(e):
        if not dest_input.value:
            status_text.value = "Please enter a destination first!"
            page.update()
            return

        status_text.value = "Generating accessible route..."
        page.update()
        
        # 1. Generate the file
        filename = await map_rendering_2.render_map(dest_input.value, [False, True])
        
        if filename:
            # 2. Open the file in a new tab on the phone
            # Since we are using assets_dir, Flet serves this file at the root /
            map_url = f"/{filename}" 
            await page.launch_url(map_url)
            
            status_text.value = "Map opened in a new tab!"
        else:
            status_text.value = "Error generating map."
        page.update()
    
        
    # --- Page Layout ---
    page.add(
        ft.Column([
            ft.Text("Step 1: Report a Hazard", size=25, weight=ft.FontWeight.BOLD),
            report_input,
            location_input,
            ft.Row([
                ft.ElevatedButton("Submit Hazard", on_click=submit_report, icon="send"), 
                loading_ring
            ]),
            
            ft.Divider(height=40, thickness=2),
            
            ft.Text("Step 2: Generate Accessible Route", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("Enter your destination to find the quietest/safest path."),
            dest_input,
            ft.ElevatedButton(
                "Render Map",
                on_click=open_map, 
                icon="map", 
                color="white", 
                bgcolor="green"
            ),
            
            ft.Container(height=20),
            status_text,
            
            # The map view element positioned at the bottom of the column
            map_view
            
        ], scroll=ft.ScrollMode.ADAPTIVE)
    )

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    absolute_assets_path = os.path.join(current_dir, "assets")
    
    # REMOVED WEB_BROWSER. Added host="0.0.0.0" so the emulator can connect.
    # Removed host="0.0.0.0" so Flet defaults to 127.0.0.1, making both the PC and emulator happy!
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550, assets_dir=absolute_assets_path)