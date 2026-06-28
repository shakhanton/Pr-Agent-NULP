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
        default="gemini-1.5-flash",
        description="Gemini model name",
        validation_alias=AliasChoices("GEMINI_MODEL", "MODEL")
    )

    model_config = SettingsConfigDict(env_prefix="")
