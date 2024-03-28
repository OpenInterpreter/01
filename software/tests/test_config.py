"""
Tests for config.py module.
"""

import os
from typing import Any

from dotenv import load_dotenv
from source.core.config import Config, get_config


def test_config_defaults() -> None:
    config = Config()
    assert not config.client.enabled
    assert config.client.url is None
    assert config.client.platform is None
    assert config.llm.service == "litellm"
    assert config.llm.model == "gpt-4"
    assert not config.llm.vision_enabled
    assert not config.llm.functions_enabled
    assert config.llm.context_window == 2048
    assert config.llm.max_tokens == 4096
    assert config.llm.temperature == 0.8
    assert not config.local.enabled
    assert not config.server.enabled
    assert config.server.host == "0.0.0.0"
    assert config.server.port == 10001
    assert config.stt.service == "openai"
    assert config.tts.service == "openai"
    assert config.tunnel.service == "ngrok"
    assert not config.tunnel.exposed


def test_config_from_dot_env(tmp_path, monkeypatch) -> None:
    env_content: str = """
    01_CLIENT_ENABLED=true
    01_CLIENT_URL=http://localhost:8000
    01_CLIENT_PLATFORM=mac
    01_LOCAL_ENABLED=true
    """
    p: Any = tmp_path / ".env"
    p.write_text(env_content)
    monkeypatch.chdir(tmp_path)
    load_dotenv(dotenv_path=str(p))

    config = Config()
    assert config.client.enabled is True
    assert config.client.url == "http://localhost:8000"
    assert config.client.platform == "mac"
    assert config.local.enabled is True


def test_config_from_dot_env_override(tmp_path, monkeypatch) -> None:
    get_config.cache_clear()
    initial_config: Config = get_config()
    assert initial_config.client.enabled is False

    env_content = """
    01_CLIENT_ENABLED=true
    """
    p: Any = tmp_path / ".env"
    p.write_text(env_content)
    monkeypatch.chdir(tmp_path)
    load_dotenv(dotenv_path=str(p))

    get_config.cache_clear()
    updated_config: Config = get_config()
    assert updated_config.client.enabled is True


def test_config_sources_yaml(tmp_path, monkeypatch) -> None:
    get_config.cache_clear()
    yaml_content = """
    llm:
        model: test
        temperature: 1.0
    server:
        port: 8080
    """
    config_path: Any = tmp_path / "config.yaml"
    config_path.write_text(yaml_content)
    monkeypatch.chdir(tmp_path)

    get_config.cache_clear()
    config: Config = get_config()
    assert config.llm.model == "test"
    assert config.llm.temperature == 1.0
    assert config.server.port == 8080


def test_config_apply_cli_args() -> None:
    config = Config()
    args: dict[str, Any] = {
        "server": True,
        "server_port": 8081,
        "model": "test",
    }
    config = Config()
    config.apply_cli_args(args)
    assert config.llm.model == "test"
    assert config.server.enabled
    assert config.server.port == 8081


def test_get_config() -> None:
    config1: Config = get_config()
    config2: Config = get_config()
    assert config1 is config2
