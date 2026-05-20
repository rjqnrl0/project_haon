import json
import logging

import boto3
from botocore.exceptions import ClientError
from functools import lru_cache
from pydantic_settings import BaseSettings

logger = logging.getLogger("v-suitcase.config")


def _load_secrets(secret_name: str, region: str) -> dict:
    try:
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        logger.error("Failed to load secrets from Secrets Manager: %s", e)
        raise


class Settings(BaseSettings):
    env: str = "local"

    # 비민감 config — .env 파일에서 로드
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "vsuitcase"
    db_username: str = "postgres"

    cognito_region: str = "ap-northeast-2"

    s3_temp_bucket: str = "v-suitcase-temp-local"
    s3_region: str = "ap-northeast-2"

    file_expiry_hours: int = 1
    share_expiry_hours: int = 720  # 30 days

    cors_origins: str = "http://localhost:5173"

    # 민감 정보 — local은 .env에서, prod/dev는 Secrets Manager에서 주입
    db_password: str = "postgres"
    cognito_pool_id: str = ""
    cognito_client_id: str = ""
    cognito_client_secret: str = ""
    openweathermap_api_key: str = ""
    unsplash_access_key: str = ""
    gemini_api_key: str = ""

    # Bedrock
    enable_bedrock: bool = False
    bedrock_region: str = "us-east-1"
    bedrock_inpaint_model: str = ""
    bedrock_remove_bg_model: str = ""

    def model_post_init(self, __context) -> None:
        if self.env in ("prod", "dev"):
            secrets = _load_secrets("v-suitcase/prod", "us-east-1")
            self.db_password = secrets.get("db_password", self.db_password)
            self.cognito_pool_id = secrets.get("cognito_pool_id", self.cognito_pool_id)
            self.cognito_client_id = secrets.get("cognito_client_id", self.cognito_client_id)
            self.cognito_client_secret = secrets.get("cognito_client_secret", self.cognito_client_secret)
            self.openweathermap_api_key = secrets.get("openweathermap_api_key", self.openweathermap_api_key)
            self.unsplash_access_key = secrets.get("unsplash_access_key", self.unsplash_access_key)
            self.gemini_api_key = secrets.get("gemini_api_key", self.gemini_api_key)

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
