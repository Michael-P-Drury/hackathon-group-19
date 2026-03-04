import flet as ft

from views.page_router import Router

def main(page: ft.Page):

    page.title = "AccessRoute - Hackathon Group 19"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30

    myRouter = Router(page, ft)

    page.on_route_change = myRouter.route_change

    page.add(
        myRouter.body
    )

    page.go('/')

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)