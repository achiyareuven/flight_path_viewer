import asyncio
from typing import List, Tuple, Optional

import flet as ft
import flet_map as map

from src.business_logic.reader import MavlinkReader
from src.utils.logger import Logger

logger = Logger.get_logger(__name__)


class MapView:
    """
    Displays the map screen with the flight path from a BIN file.
    Calls MavlinkReader to load GPS data and draw it on the map.
    """
    def __init__(self,page)-> None:
        self.page=page
        self.page.title = " path map "

        self.status_text = ft.Text("points loading… ")
        self.progress_bar = ft.ProgressBar(width=320, value=None)

        self.polyline_ref: ft.Ref[map.PolylineLayer] = ft.Ref[map.PolylineLayer]()
        self.marker_ref: ft.Ref[map.MarkerLayer] = ft.Ref[map.MarkerLayer]()

        self.flight_map = self._build_map(self.polyline_ref, self.marker_ref)

        # start loading if path exists
        file_path: Optional[str] = self.page.session.get("file_path")
        if not file_path:
            logger.warning("No file path found in session — show fallback.")
            self._fallback_view = self._build_no_file_view()
            self._layout = None
        else:
            logger.info(f"Opening map view for file: {file_path}")
            self._fallback_view = None
            self._layout = self._build_layout(
                self._build_back_button(),
                self.status_text,
                self.progress_bar,
                self.flight_map,
            )

            async def task():
                await self._load_and_draw_async(
                    file_path, self.flight_map, self.polyline_ref, self.marker_ref,
                    self.status_text, self.progress_bar, self.page
                )

            # run async task
            self.page.run_task(task)

    def view(self) -> ft.View:
        if self._fallback_view:
            return self._fallback_view
        return ft.View(route="/map", controls=[ft.Container(self._layout, padding=10, expand=True)])

    async def _load_and_draw_async(
        self,
        file_path: str,
        flight_map: map.Map,
        polyline_ref: ft.Ref[map.PolylineLayer],
        marker_ref: ft.Ref[map.MarkerLayer],
        status_text: ft.Text,
        progress_bar: ft.ProgressBar,
        page: ft.Page,
    ):
        """Loads the GPS points from the file, draws the route on the map, and updates the UI."""
        try:
            logger.info(f"Starting to read GPS data from {file_path}")
            reader = MavlinkReader(file_path)
            points: List[Tuple[float, float]] = await asyncio.to_thread(reader.read_gps_data)

            if not points:
                status_text.value = "לא נמצאו נקודות בקובץ."
                logger.warning("No GPS points found in file.")
                return

            logger.info(f"Successfully read {len(points)} GPS points.")
            self._draw_path_on_map(points, flight_map, polyline_ref, marker_ref)
            status_text.value = f"נטענו {len(points)} נקודות"

        except Exception as ex:
            status_text.value = f"שגיאה בקריאת הקובץ: {ex}"
            logger.error(f"Error while reading or drawing file '{file_path}': {ex}", exc_info=True)

        finally:
            progress_bar.visible = False
            page.update()
            logger.debug("Map rendering completed, progress bar hidden.")

    def _draw_path_on_map(
        self,
        points: List[Tuple[float, float]],
        flight_map: map.Map,
        polyline_ref: ft.Ref[map.PolylineLayer],
        marker_ref: ft.Ref[map.MarkerLayer],
    ):

        coords = [map.MapLatitudeLongitude(lat, lng) for lat, lng in points]

        # path line
        polyline_ref.current.polylines = [
            map.PolylineMarker(
                coordinates=coords,
                border_stroke_width=3,
                border_color=ft.Colors.BLUE,
                color=ft.Colors.with_opacity(0.35, ft.Colors.BLUE),
            )
        ]


        marker_ref.current.markers = [
            map.Marker(
                content=ft.Icon(ft.Icons.PLAY_ARROW, color=ft.Colors.GREEN),
                coordinates=coords[0],
            ),
            map.Marker(
                content=ft.Icon(ft.Icons.FLAG, color=ft.Colors.RED),
                coordinates=coords[-1],
            ),
        ]

        # move map to start point
        flight_map.move_to(destination=coords[0], zoom=10)


    def _build_map(self, polyline_ref: ft.Ref[map.PolylineLayer], marker_ref: ft.Ref[map.MarkerLayer]) -> map.Map:
        """Creates the map object with base layers."""
        logger.debug("Building base map with TileLayer, PolylineLayer, and MarkerLayer.")

        return map.Map(
            expand=True,
            initial_center=map.MapLatitudeLongitude(31, 36),
            initial_zoom=8,
            interaction_configuration=map.MapInteractionConfiguration(
                flags=map.MapInteractiveFlag.ALL
            ),
            layers=[
                map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=lambda e: logger.warning(f"TileLayer Error: {e}"),
                ),
                map.PolylineLayer(ref=polyline_ref, polylines=[]),
                map.MarkerLayer(ref=marker_ref, markers=[]),
            ]
        )
    def _build_back_button(self) -> ft.OutlinedButton:
        """Creates a back button to the main screen."""
        return ft.OutlinedButton("beck", icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go("/"))

    def _build_layout(self, back_button, status_text, progress_bar, flight_map) -> ft.Column:
        return ft.Column(
            controls=[
                ft.Row([back_button], alignment=ft.MainAxisAlignment.START),
                status_text,
                progress_bar,
                ft.Container(flight_map, expand=True),
            ],
            expand=True,
            spacing=10,
        )

    def _build_no_file_view(self) -> ft.View:
        return ft.View(
            route="/map",
            controls=[
                ft.Column(
                    [
                        ft.Text("no file selected. return to the main screen."),
                        ft.OutlinedButton("beck", icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                    ],
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
        )

