import flet as ft
import flet_webview as fwv
import genai_call
import map_rendering_2
import os


def HomeView(page, ft=ft):
    
    # --- 1. Define UI Elements FIRST ---
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
    map_view = fwv.WebView(height=600, visible=False)


    # --- 2. Define Event Handlers SECOND ---
    async def submit_report(e):
        if not report_input.value or not location_input.value:
            status_text.value = "Please fill in both hazard fields!"
            page.update()
            return

        loading_ring.visible = True
        status_text.value = "Analyzing hazard with Cerebras AI..."
        page.update()

        # Assuming genai_call is available in this scope
        success = await genai_call.create_report(report_input.value, location_input.value)
        
        loading_ring.visible = False
        if success:
            status_text.value = "Hazard report saved successfully!"
            report_input.value = ""
            location_input.value = ""
        else:
            status_text.value = "Error processing report. Check API Key/Connection."
        
        page.update()


    async def open_map(e):
        if not dest_input.value:
            status_text.value = "Please enter a destination first!"
            page.update()
            return

        status_text.value = "Generating accessible route..."
        page.update()
        
        needs_visual_routing = visual_cb.value
        needs_sensory_routing = sensory_cb.value
        # 1. Generate the file
        filename = await map_rendering_2.render_map(dest_input.value, [visual_cb.value, sensory_cb.value])
        
        if filename:
            # 2. Open the file in a new tab on the phone
            map_url = f"/{filename}" 
            await page.launch_url(map_url)
            
            status_text.value = "Map opened in a new tab!"
        else:
            status_text.value = "Error generating map."
        page.update()


    # --- 3. Build the Layout THIRD ---
    # Now that everything is defined, assemble it inside the Column

    visual_cb = ft.Checkbox(label="Visual Impairment", value=False)
    sensory_cb = ft.Checkbox(label="Sensory Considerations", value=False)   
    content = ft.Column([        
        ft.Text("Where would you like to go ?", size=25, weight=ft.FontWeight.BOLD),
        ft.Text("Accessibility options", size=20, weight=ft.FontWeight.BOLD),
        visual_cb,
        sensory_cb,
        ft.Text("Enter your destination to find the quietest/safest path."),
        dest_input,
        ft.ElevatedButton(
            "Generate route",
            on_click=open_map, 
            icon="map", 
            color="white", 
            bgcolor="#1d4289"
        ),
        # ft.Container(height=10),
        status_text,

        ft.Divider(height=5, thickness=2),

        ft.Text("Report a Hazard", size=25, weight=ft.FontWeight.BOLD),
        report_input,
        location_input,
        ft.Row([
            ft.ElevatedButton("Submit Hazard",
            on_click=submit_report,
            icon="send",
            color="white", 
            bgcolor="#d3273e"),
            loading_ring
        ]),
        
        # ft.Divider(height=40, thickness=2),
        
        # ft.Text("Step 2: Generate Accessible Route", size=25, weight=ft.FontWeight.BOLD),
        # visual_cb,
        # sensory_cb,
        # ft.Text("Enter your destination to find the quietest/safest path."),
        # dest_input,
        # ft.ElevatedButton(
        #     "Render Map",
        #     on_click=open_map, 
        #     icon="map", 
        #     color="white", 
        #     bgcolor="green"
        # ),
        
        # ft.Container(height=20),
        # status_text,
        
        # The map view element positioned at the bottom of the column
        map_view
    ], scroll=ft.ScrollMode.ADAPTIVE)


    # 4. Return the View FINALLY
    return content