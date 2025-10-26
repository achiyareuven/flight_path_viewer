import pandas as pd
from pymavlink import mavutil

from src.config import settings
from src.utils.logger import Logger

logger = Logger.get_logger(name=__name__)


class BinReader:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.msg_type = settings.MAVLINK_TYPE_MSG
        self.msg_id_field = settings.MAVLINK_MSG_ID
        self.main_gps_value = settings.MAVLINK_MAIN_GPS
        self.log = None

        try:
            self.log = mavutil.mavlink_connection(self.file_path)
            logger.info(f"MavlinkReader initialized with file: {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to initialize MavlinkReader: {e}")

    def run_get_sample_df(self) -> pd.DataFrame:
        df: pd.DataFrame = self.read_gps_data()
        df_sample: pd.DataFrame = self.sample_every_n_df(df, 1)
        return df_sample

    def read_gps_data(self) -> pd.DataFrame:
        """
        reads GPS data from the mavlink log file
        returns a list of (lat, lng) tuples
        """
        gps_data: list = []
        if not self.log:
            logger.warning("MavlinkReader not initialized properly")
            return pd.DataFrame(gps_data, columns=["lat", "lng"])

        try:
            while True:
                msg = self.log.recv_match(type=self.msg_type, blocking=False)
                if msg is None:
                    break

                gps_id = getattr(msg, self.msg_id_field, None)
                if gps_id != self.main_gps_value:
                    continue

                lat = getattr(msg, "Lat", None)
                lng = getattr(msg, "Lng", None)
                if lat is None or lng is None:
                    continue

                gps_data.append((lat, lng))
            df = pd.DataFrame(gps_data, columns=["lat", "lng"])
            logger.info(f"Read {len(df)} GPS points from the log")
            return df

        except Exception as e:
            logger.error(f"Error reading GPS data: {e}")

        finally:
            if self.log:
                self.log.close()


    def sample_every_n_df(self, df: pd.DataFrame, n: int) -> pd.DataFrame:

        if df is None or df.empty or n <= 1:
            return df
        return df.iloc[::n].reset_index(drop=True)
