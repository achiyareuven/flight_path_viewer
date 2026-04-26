import flet as ft

from src.gui.app_router import AppRouter


def main(page: ft.Page) -> None:
    router = AppRouter(page)
    page.go("/")


if __name__ == "__main__":
    ft.app(target=main)
