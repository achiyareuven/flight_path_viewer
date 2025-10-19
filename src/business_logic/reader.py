from pymavlink import mavutil
from src.utils.logger import Logger

logger = Logger.get_logger(name=__name__)

class MavlinkReader:
    """
    read file and extract GPS data
    1. init with file path
    2. read GPS messages and return list of coordinates
    3. each coordinate is a tuple (lat, lng)
    4. only messages with I==1 are considered valid
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.log = None

        try:
            self.log = mavutil.mavlink_connection(self.file_path)
            logger.info(f"MavlinkReader initialized with file: {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to initialize MavlinkReader: {e}")

    def read_gps_data(self) -> list[dict]:
        """
        קורא את כל ההודעות מסוג GPS ומחזיר רשימת נ״צ:
        [{"lat": float, "lng": float}, ...]
        """
        gps_data: list = []

        if not self.log:
            logger.warning("MavlinkReader not initialized properly")
            return gps_data

        try:
            while True:
                msg = self.log.recv_match(type="GPS")
                if msg is None:
                    break

                if getattr(msg, "I", None) != 1:
                    continue

                lat = getattr(msg, "Lat", None)
                lng = getattr(msg, "Lng", None)
                if lat is None or lng is None:
                    continue

                if lat is None or lng is None:
                    continue

                gps_data.append((lat,  lng))

                if len(gps_data) % 1000 == 0:
                    logger.debug(f"Collected {len(gps_data)} GPS points so far...")

        except Exception as e:
            logger.error(f"Error reading GPS data: {e}")

        logger.info(f"Total GPS points extracted: {len(gps_data)}")
        return gps_data




