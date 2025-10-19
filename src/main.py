
import flet as ft
from src.gui.home_page import HomeView
from src.gui.map_page import MapView


class AppRouter:
    """
    manages routing between different views in the application
    1. initializes with flet.Page
    2. sets up route change and view pop events
    3. starts at home view
    """

    def __init__(self, page: ft.Page)-> None:
        self.page = page

        self.page.window_min_width = 900
        self.page.window_min_height = 600
        self.page.theme_mode = ft.ThemeMode.DARK


        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

    def start(self)-> None:
        self.page.go("/")

    # ---------- Events ----------
    def route_change(self, e: ft.RouteChangeEvent)-> None:
        self.page.views.clear()

        if self.page.route == "/":
            self.page.views.append(HomeView(self.page).view())
        elif self.page.route == "/map":
            self.page.views.append(MapView(self.page).view())
        else:
            self.page.views.append(HomeView(self.page).view())

        self.page.update()

    def view_pop(self, e: ft.ViewPopEvent)-> None:
        self.page.views.pop()
        self.page.update()


def main(page: ft.Page)-> None:
    AppRouter(page).start()


if __name__ == "__main__":
    ft.app(target=main)

