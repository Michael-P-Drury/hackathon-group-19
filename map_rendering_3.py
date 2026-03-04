import os
import flet as ft
import flet_webview as fwv
import genai_call
import map_rendering_2

class AccessRouteApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.configure_page()
        
        # --- UI Component Definitions ---
        self.report_input = ft.TextField(
            label="What is the issue?",
            hint_text="e.g. Construction site with loud drilling",
            multiline=True,
        )
        self.location_input = ft.TextField(
            label="Hazard Location", 
            hint_text="e.g. Queen Street, Cardiff"
        )
        self.dest_input = ft.TextField(
            label="Where are you going?",
            hint_text="e.g. Cardiff Central Station",
            value="Cardiff Castle",
        )
        
        self.status_text = ft.Text(value="", color=ft.colors.BLUE_500, weight=ft.FontWeight.W_500)
        self.loading_ring = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2)
        self.map_view = fwv.WebView(height=600, visible=False)

    def configure_page(self):
        """Sets initial page properties."""
        self.page.title = "AccessRoute - Hackathon Group 19"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 30
        self.page.scroll = ft.ScrollMode.ADAPTIVE

    def update_status(self, message: str, is_error: bool = False):
        """Centralized status updates."""
        self.status_text.value = message
        self.status_text.color = ft.colors.RED if is_error else ft.colors.BLUE_500
        self.page.update()

    async def handle_submit_report(self, e):
        """Logic for submitting hazard reports via AI."""
        if not self.report_input.value or not self.location_input.value:
            self.update_status("Please fill in both hazard fields!", is_error=True)
            return

        self.loading_ring.visible = True
        self.update_status("Analyzing hazard with Cerebras AI...")

        try:
            success = await genai_call.create_report(
                self.report_input.value, 
                self.location_input.value
            )
            
            if success:
                self.update_status("Hazard report saved successfully!")
                self.report_input.value = ""
                self.location_input.value = ""
            else:
                self.update_status("Error processing report. Check API Connection.", is_error=True)
        finally:
            self.loading_ring.visible = False
            self.page.update()

    async def handle_open_map(self, e):
        """Logic for generating and launching the map."""
        if not self.dest_input.value:
            self.update_status("Please enter a destination first!", is_error=True)
            return

        self.update_status("Generating accessible route...")
        
        # Note: render_map should save the file into the 'assets' directory
        filename = await map_rendering_2.render_map(self.dest_input.value, [False, True])
        
        if filename:
            # Flet serves files in the assets folder at the root path '/'
            map_url = f"/{filename}"
            await self.page.launch_url(map_url)
            self.update_status("Map opened in a new tab!")
        else:
            self.update_status("Error generating map.", is_error=True)

    def build_ui(self):
        """Constructs the main layout."""
        layout = ft.Column([
            ft.Text("Step 1: Report a Hazard", size=25, weight=ft.FontWeight.BOLD),
            self.report_input,
            self.location_input,
            ft.Row([
                ft.ElevatedButton(
                    "Submit Hazard", 
                    on_click=self.handle_submit_report, 
                    icon=ft.icons.SEND
                ),
                self.loading_ring
            ]),
            
            ft.Divider(height=40, thickness=2),
            
            ft.Text("Step 2: Generate Accessible Route", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("Enter your destination to find the quietest/safest path."),
            self.dest_input,
            ft.ElevatedButton(
                "Render Map",
                on_click=self.handle_open_map,
                icon=ft.icons.MAP,
                color=ft.colors.WHITE,
                bgcolor=ft.colors.GREEN_700
            ),
            
            ft.Container(height=20),
            self.status_text,
            self.map_view
        ])
        
        self.page.add(layout)

async def main(page: ft.Page):
    app = AccessRouteApp(page)
    app.build_ui()

if __name__ == "__main__":
    # Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(current_dir, "assets")
    
    # Ensure assets directory exists
    if not os.path.exists(assets_path):
        os.makedirs(assets_path)

    # Launch app
    # Port 8550 is used; assets_dir enables Flet to serve the HTML files
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER, 
        port=8550, 
        assets_dir=assets_path
    )
