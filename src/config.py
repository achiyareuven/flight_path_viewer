from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    MAVLINK_TYPE_MSG: str = Field("GPS", description="Message type to read from the MAVLink log")
    MAVLINK_MSG_ID: str = Field("I", description="Field name for GPS instance identifier")
    MAVLINK_MAIN_GPS: int = Field(1, description="Value of the main GPS instance to read")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = AppSettings()
