from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    env: str = "local"

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "vsuitcase"
    db_username: str = "postgres"
    db_password: str = "postgres"

    cognito_pool_id: str = ""
    cognito_client_id: str = ""
    cognito_client_secret: str = ""
    cognito_region: str = "ap-northeast-2"

    s3_temp_bucket: str = "v-suitcase-temp-local"
    s3_region: str = "ap-northeast-2"

    file_expiry_hours: int = 1
    share_expiry_hours: int = 720  # 30 days

    cors_origins: str = "http://localhost:5173"

    openweathermap_api_key: str = ""
    unsplash_access_key: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
