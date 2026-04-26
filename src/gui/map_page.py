import asyncio
from typing import Optional

import flet as ft
import flet_map as fmap
import pandas as pd

from src.business_logic.bin_reader import BinReader
from src.utils.logger import Logger

logger = Logger.get_logger(__name__)


class MapPage:
    """
    Displays the map screen with the flight path from a BIN file.
    Handles asynchronous loading of GPS points and updates the UI accordingly.
    """

    def __init__(self, page: ft.Page) -> None:
        """Initialize the map view and its UI elements."""
        self.page = page
        self.page.title = "path map"

        self.status_text = ft.Text("points loading…")
        self.progress_bar = ft.ProgressBar(width=320, value=None, visible=True)

        self.polyline_ref: ft.Ref[fmap.PolylineLayer] = ft.Ref[fmap.PolylineLayer]()
        self.marker_ref: ft.Ref[fmap.MarkerLayer] = ft.Ref[fmap.MarkerLayer]()
        self.flight_map: fmap.Map = self._build_map(self.polyline_ref, self.marker_ref)

        self.page.run_task(self._load_and_draw_async)

    def build(self) -> list[ft.Control]:
        """Assembles the map view layout (toolbar, status, progress, map)."""
        top_bar = ft.Row(
            controls=[self._build_back_button()],
            alignment=ft.MainAxisAlignment.START,
        )

        return [
            top_bar,
            self.status_text,
            self.progress_bar,
            ft.Container(self.flight_map, expand=True),
        ]

    async def _load_and_draw_async(self) -> None:
        try:
            self._update_status("Loading GPS points…", show_progress=True)
            file_path: Optional[str] = self.page.session.get("file_path")
            if not file_path:
                self._update_status("No file selected.", show_progress=False)
                return

            points = await asyncio.to_thread(self.get_points)

            if points.empty:
                self._update_status("No GPS points found in the file.", show_progress=False)
                return

            self._draw_path_on_map(points)
            self._update_status(f"Loaded {len(points)} points.", show_progress=False)
        except Exception as ex:
            logger.error(f"Error while drawing map: {ex}", exc_info=True)
            self._update_status("Error drawing the map.", show_progress=False)

    def _draw_path_on_map(self, points: pd.DataFrame) -> None:
        if points.empty:
            return

        coords = [fmap.MapLatitudeLongitude(lat, lng) for lat, lng in zip(points["lat"], points["lng"])]

        self.polyline_ref.current.polylines = [
            fmap.PolylineMarker(
                coordinates=coords,
                border_stroke_width=3,
                border_color=ft.Colors.BLUE,
                color=ft.Colors.with_opacity(0.35, ft.Colors.BLUE),
            )
        ]

        self.marker_ref.current.markers = [
            fmap.Marker(
                content=ft.Icon(ft.Icons.PLAY_ARROW, tooltip="Start", color=ft.Colors.GREEN),
                coordinates=coords[0],
            ),
            fmap.Marker(
                content=ft.Icon(ft.Icons.FLAG, tooltip="End", color=ft.Colors.RED),
                coordinates=coords[-1],
            ),
        ]

        self.flight_map.move_to(destination=coords[0], zoom=10)
        self.page.update()

    def _build_map(
        self,
        polyline_ref: ft.Ref[fmap.PolylineLayer],
        marker_ref: ft.Ref[fmap.MarkerLayer],
    ) -> fmap.Map:
        return fmap.Map(
            expand=True,
            initial_center=fmap.MapLatitudeLongitude(31.0, 36.0),
            initial_zoom=8,
            interaction_configuration=fmap.MapInteractionConfiguration(flags=fmap.MapInteractiveFlag.ALL),
            layers=[
                fmap.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                ),
                fmap.PolylineLayer(ref=polyline_ref, polylines=[]),
                fmap.MarkerLayer(ref=marker_ref, markers=[]),
            ],
        )

    def get_points(self) -> pd.DataFrame:
        try:
            file_path: Optional[str] = self.page.session.get("file_path")
            if not file_path:
                logger.warning("get_points called without a file_path in session.")
                return pd.DataFrame(columns=["lat", "lng"])

            reader = BinReader(file_path)
            points = reader.run_get_sample_df()

            if points.empty:
                logger.info("No GPS points extracted from the file.")
                return pd.DataFrame(columns=["lat", "lng"])

            return points
        except Exception as ex:
            logger.error(f"Error while reading points: {ex}", exc_info=True)
            return pd.DataFrame(columns=["lat", "lng"])

    def _build_back_button(self) -> ft.OutlinedButton:
        return ft.OutlinedButton(
            text="back",
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda _: self.page.go("/"),
        )

    def _update_status(self, message: str, show_progress: bool = True) -> None:
        self.status_text.value = message
        self.progress_bar.visible = show_progress
        self.page.update()
