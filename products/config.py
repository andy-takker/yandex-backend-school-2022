import logging
import os
from functools import lru_cache
from typing import Optional, Any, Dict

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    DEBUG: bool
    VERSION: str = '0.0.1'
    SERVER_NAME: str
    PROJECT_NAME: str
    API_PREFIX: str = ''
    ALLOWED_HOSTS: str = None

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator('SQLALCHEMY_DATABASE_URI', pre=True)
    def assemble_db_connection(cls, v: Optional[str],
                               values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme='postgresql+psycopg2',
            user=values.get('POSTGRES_USER'),
            password=values.get('POSTGRES_PASSWORD'),
            host=values.get('POSTGRES_HOST'),
            path=f'/{values.get("POSTGRES_DB") or ""}',
            port=f'{values.get("POSTGRES_PORT") or ""}',
        )


@lru_cache()
def get_settings():
    return Settings(_env_file=os.getenv('ENV_FILE', '../.env'))
