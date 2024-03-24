"""
Application configuration model.
"""

import os
from functools import lru_cache
from typing import Any

from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from source.core.models import LLM, STT, TTS, Client, Local, Server, Tunnel

APP_PREFIX: str = os.getenv("01_PREFIX", "01_")


class Config(BaseSettings):
    """
    Base configuration model
    """

    client: Client = Client()
    llm: LLM = LLM()
    local: Local = Local()
    server: Server = Server()
    stt: STT = STT()
    tts: TTS = TTS()
    tunnel: Tunnel = Tunnel()

    model_config = SettingsConfigDict(extra="allow")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Modify the order of precedence for settings sources.
        """
        return (
            DotEnvSettingsSource(
                settings_cls,
                env_prefix=APP_PREFIX,
                env_file=".env",
                env_file_encoding="utf-8",
                env_nested_delimiter="_",
            ),
            YamlConfigSettingsSource(
                settings_cls,
                yaml_file=os.getenv(f"{APP_PREFIX}CONFIG_FILE", "config.yaml"),
            ),
        )

    def apply_cli_args(self, args: dict) -> None:
        """
        Apply CLI arguments to config.
        """
        mapping: dict[str, str] = {
            "server": "server.enabled",
            "server_host": "server.host",
            "server_port": "server.port",
            "tunnel_service": "tunnel.service",
            "expose": "tunnel.exposed",
            "client": "client.enabled",
            "server_url": "client.url",
            "client_type": "client.platform",
            "llm_service": "llm.service",
            "model": "llm.model",
            "llm_supports_vision": "llm.vision_enabled",
            "llm_supports_functions": "llm.functions_enabled",
            "context_window": "llm.context_window",
            "max_tokens": "llm.max_tokens",
            "temperature": "llm.temperature",
            "tts_service": "tts.service",
            "stt_service": "stt.service",
            "local": "local.enabled",
        }

        for key, path in mapping.items():
            if key in args and args[key] is not None:
                self.set_field(path, args[key])

    def set_field(self, field: str, value: Any) -> None:
        """
        Set field value
        """
        obj: Any = self
        parts: list[str] = field.split(".")

        for part in parts[:-1]:
            obj: Any = getattr(obj, part)

        setattr(obj, parts[-1], value)


@lru_cache()
def get_config() -> Config:
    """
    Return the application configuration.
    """
    return Config()
