import flet as ft

from src.gui.home_page import HomePage
from src.gui.map_page import MapPage


class AppRouter:
    """
    manages routing between different views in the application
    1. initializes with flet.Page
    2. sets up route change and view pop events
    3. starts at home view
    """

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.page.window_min_width = 900
        self.page.window_min_height = 600
        self.page.theme_mode = ft.ThemeMode.DARK

        self.page.on_route_change = self.route_change

    # ---------- Events ----------
    def route_change(self, _: ft.RouteChangeEvent) -> None:
        self.page.views.clear()
        if self.page.route == "/":
            home_screen = HomePage(self.page)
            self.page.views.append(ft.View("/", controls=home_screen.build()))

        elif self.page.route == "/map":
            map_screen = MapPage(self.page)
            self.page.views.append(ft.View("/map", controls=map_screen.build()))

        else:
            home_screen = HomePage(self.page)
            self.page.views.append(ft.View("/", controls=home_screen.build()))

        self.page.update()
