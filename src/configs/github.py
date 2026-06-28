import json

from pydantic import Field, AliasChoices, model_validator
from pydantic_settings import SettingsConfigDict

from .base import BaseApplicationConfig


class GitHubConfig(BaseApplicationConfig):
    GITHUB_TOKEN: str = Field(
        ...,
        description="GitHub Token for API access",
        validation_alias=AliasChoices("GITHUB_TOKEN", "GIT_TOKEN")
    )
    REPOSITORY: str = Field(
        ...,
        description="GitHub Repository in owner/repo format",
        validation_alias=AliasChoices("GIT_REPOSITORY", "GITHUB_REPOSITORY")
    )
    LAB_PATH_RULES: dict = Field(
        default_factory=dict,
        description="Mapping of lab names to file path prefixes",
        validation_alias=AliasChoices("LAB_PATH_RULES")
    )
    MAX_ATTEMPTS: int = Field(
        default=3,
        description="Maximum number of submission attempts per lab",
        validation_alias=AliasChoices("MAX_ATTEMPTS")
    )

    model_config = SettingsConfigDict(env_prefix="")

    @model_validator(mode="before")
    @classmethod
    def parse_lab_path_rules(cls, values):
        rules = values.get("LAB_PATH_RULES") or values.get("lab_path_rules")
        if isinstance(rules, str):
            values["LAB_PATH_RULES"] = json.loads(rules)
        return values
