"""
Application configuration models.
"""

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

APP_PREFIX = "01_"


class Client(BaseModel):
    """
    Client configuration model
    """

    enabled: bool = False
    url: None | str = None
    platform: str = "auto"


class LLM(BaseModel):
    """
    LLM configuration model
    """

    service: str = "litellm"
    model: str = "gpt-4"
    vision_enabled: bool = False
    functions_enabled: bool = False
    context_window: int = 2048
    max_tokens: int = 4096
    temperature: float = 0.8


class Local(BaseModel):
    """
    Local configuration model
    """

    enabled: bool = False
    tts_service: str = "piper"
    stt_service: str = "local-whisper"


class Server(BaseModel):
    """
    Server configuration model
    """

    enabled: bool = False
    host: str = "0.0.0.0"
    port: int = 10001


class STT(BaseModel):
    """
    Speech-to-text configuration model
    """

    service: str = "openai"


class TTS(BaseModel):
    """
    Text-to-speech configuration model
    """

    service: str = "openai"


class Tunnel(BaseModel):
    """
    Tunnel configuration model
    """

    service: str = "ngrok"
    exposed: bool = False


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

    model_config = SettingsConfigDict(
        env_prefix=APP_PREFIX,
        env_file=".env",
        env_file_encoding="utf-8",
        yaml_file="config.yaml",
    )

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
        return (YamlConfigSettingsSource(settings_cls),)
