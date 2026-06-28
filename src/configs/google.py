from json import loads

from pydantic import Field, model_validator, AliasChoices
from pydantic_settings import SettingsConfigDict
from loguru import logger

from .base import BaseApplicationConfig


class GoogleSheetsConfig(BaseApplicationConfig):
    CREDENTIALS_CONTENT: str | dict = Field(
        ...,
        description="Google credentials content",
        validation_alias=AliasChoices("GOOGLE_CREDENTIALS_CONTENT", "CREDENTIALS_CONTENT")
    )
    SPREADSHEET_URL: str = Field(
        ...,
        description="Google Spreadsheet URL",
        validation_alias=AliasChoices("GOOGLE_SPREADSHEET_URL", "SPREADSHEET_URL")
    )

    model_config = SettingsConfigDict(env_prefix="")

    @model_validator(mode="before")
    def load_credentials(cls, values):
        credentials = values.get("CREDENTIALS_CONTENT")
        if isinstance(credentials, str):
            if credentials.endswith(".json"):
                with open(credentials, "r", encoding="utf-8") as credentials_file:
                    content = credentials_file.read()
                    values["CREDENTIALS_CONTENT"] = loads(content)
                    logger.info("Credentials loaded from file")
            else:
                try:
                    values["CREDENTIALS_CONTENT"] = loads(credentials)
                except Exception as e:
                    logger.error(f"Error parsing credentials JSON: {e}")
                    raise
        return values
