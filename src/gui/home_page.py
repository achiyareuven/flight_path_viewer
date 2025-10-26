from typing import Optional

import flet as ft

from src.utils.logger import Logger

logger = Logger.get_logger(name=__name__)


class HomePage:
    """
    Page for selecting a .bin flight file
    Saves the path in session and navigates to /map
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Select flight file (.bin)"
        self.status_text = ft.Text("No file selected", selectable=True, color=ft.Colors.GREEN_400)

        self._setup_file_picker()

    def on_file_result(self, e: ft.FilePickerResultEvent) -> None:
        if not e.files:
            self._update_status("Selection cancelled", ft.Colors.ORANGE_400)
            return

        file: ft.FilePickerFile = e.files[0]
        file_path: Optional[str] = getattr(file, "path", None)

        if not file_path:
            self._update_status("Cannot read file path.", ft.Colors.RED_400)
            self.page.update()
            return

        self._update_status(f"Selected: {file_path}", ft.Colors.GREEN_400)
        self.page.session.set("file_path", file_path)
        self.page.update()
        self.page.go("/map")

    def _setup_file_picker(self) -> None:
        """Initializes and attaches the FilePicker to the page overlay."""
        self.file_picker = ft.FilePicker(on_result=self.on_file_result)

        if self.file_picker not in self.page.overlay:
            self.page.overlay.append(self.file_picker)
            self.page.update()

    def on_pick_click(self, _: ft.ControlEvent) -> None:
        self.file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["bin"],
        )

    def _update_status(self, message: str, color: str) -> None:
        """Update the status text and refresh the page."""
        self.status_text.value = message
        self.status_text.color = color
        self.page.update()

    def build(self) -> list[ft.Control]:
        pick_btn = ft.FilledButton(
            "choose file BIN",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.on_pick_click,
        )

        content = ft.Column(
            controls=[
                ft.Text(" Select a flight file in .bin format. ", size=18, weight=ft.FontWeight.BOLD),
                pick_btn,
                self.status_text,
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

        return [
            ft.Stack(
                expand=True,
                controls=[
                    ft.Image(
                        src=r"C:\Users\achiy\Downloads\pngtree-drone-flying-over-a-mountain-at"
                        r"-sunset-picture-image_2881970.jpg",
                        fit=ft.ImageFit.COVER,
                        expand=True,
                    ),
                    ft.Container(
                        content,
                        padding=20,
                        expand=True,
                        alignment=ft.alignment.center,
                    ),
                ],
            )
        ]
