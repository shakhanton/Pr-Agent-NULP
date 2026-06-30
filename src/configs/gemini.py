from pydantic import Field, AliasChoices
from pydantic_settings import SettingsConfigDict

from .base import BaseApplicationConfig


class GeminiConfig(BaseApplicationConfig):
    API_KEY: str = Field(
        ...,
        description="Google Gemini API Key",
        validation_alias=AliasChoices("GEMINI_API_KEY", "API_KEY")
    )
    MODEL: str = Field(
        default="gemini-2.5-flash-lite",
        description="Gemini model name",
        validation_alias=AliasChoices("GEMINI_MODEL", "MODEL")
    )

    model_config = SettingsConfigDict(env_prefix="")
