import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HOSTNAME: str
    PORT: int
    TIMEOUT: int
    MAX_CONNECTIONS: int

    @property
    def web_config(self) -> dict:
        return {'host': self.HOSTNAME,
                'port': self.PORT,
                'timeout': self.TIMEOUT,
                'max_connections': self.MAX_CONNECTIONS,
                }

settings = Settings(_env_file='.env')