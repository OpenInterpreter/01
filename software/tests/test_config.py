"""
Tests for config.py module.
"""

from typing import Any

from dotenv import load_dotenv

from source.core.config import APP_PREFIX, Config, get_config


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
    env_content = f"""
    {APP_PREFIX}CLIENT_ENABLED=true
    {APP_PREFIX}CLIENT_URL=http://localhost:8000
    {APP_PREFIX}CLIENT_PLATFORM=mac
    {APP_PREFIX}LOCAL_ENABLED=true
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


def test_config_sources_yaml(tmp_path, monkeypatch):
    yaml_content = """
    llm:
        model: test
        temperature: 1.0
    server:
        port: 8080
    """
    p: Any = tmp_path / "config.yaml"
    p.write_text(yaml_content)
    monkeypatch.setenv("01_CONFIG_FILE", str(p))

    config = Config()
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
