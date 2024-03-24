"""
Application models.
"""

from pydantic import BaseModel


class Client(BaseModel):
    """
    Client configuration model
    """

    enabled: bool = False
    url: str | None = None
    platform: str | None = None


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
