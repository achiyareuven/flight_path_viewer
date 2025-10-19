import flet as ft
from typing import Optional

class HomeView:
    """
    Page for selecting a .bin flight file
    Saves the path in session and navigates to /map
    """
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Select flight file (.bin)"

        self.selected_text = ft.Text("No file selected", selectable=True)
        self.error_text = ft.Text("", color=ft.Colors.RED_500)

        self.file_picker = ft.FilePicker(on_result=self.on_file_result)
        self.page.overlay.append(self.file_picker)


    def on_file_result(self, e: ft.FilePickerResultEvent)-> None:
        self.error_text.value = ""
        if not e.files:
            self.selected_text.value = "Selection cancelled"
            self.page.update()
            return

        file: ft.FilePickerFile = e.files[0]
        file_path: Optional[str] = getattr(file,"path", None)

        if not file_path:
            self.error_text.value = "Cannot read file path."
            self.page.update()
            return

        self.selected_text.value = f"Selected: {file_path}"
        self.page.session.set("file_path", file_path)
        self.page.update()
        self.page.go("/map")

    def on_pick_click(self,_)-> None:
        self.file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["bin"],
        )


    def view(self) -> ft.View:
        pick_btn = ft.FilledButton(
            "choose file BIN",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.on_pick_click,
        )

        content = ft.Column(
            controls=[
                ft.Text(" Select a flight file in .bin format. ",
                        size=18, weight=ft.FontWeight.BOLD),
                pick_btn,
                self.selected_text,
                self.error_text,
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

        return ft.View(
            route="/",
            padding=0,
            controls=[
                ft.Stack(
                    expand=True,
                    controls=[
                        ft.Image(
                            src=r"C:\Users\achiy\Downloads\pngtree-drone-flying-over-a-mountain-at-sunset-picture-image_2881970.jpg",
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
            ],
        )

