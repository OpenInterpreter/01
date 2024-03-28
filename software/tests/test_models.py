from source.core.models import LLM, STT, TTS, Client, Local, Server, Tunnel


def test_client_model() -> None:
    client = Client()
    assert not client.enabled
    assert client.url is None
    assert client.platform is None


def test_llm_model() -> None:
    llm = LLM()
    assert llm.service == "litellm"
    assert llm.model == "gpt-4"
    assert not llm.vision_enabled
    assert not llm.functions_enabled
    assert llm.context_window == 2048
    assert llm.max_tokens == 4096
    assert llm.temperature == 0.8


def test_local_model() -> None:
    local = Local()
    assert not local.enabled


def test_server_model() -> None:
    server = Server()
    assert not server.enabled
    assert server.host == "0.0.0.0"
    assert server.port == 10001


def test_stt_model() -> None:
    stt = STT()
    assert stt.service == "openai"


def test_tts_model() -> None:
    tts = TTS()
    assert tts.service == "openai"


def test_tunnel_model() -> None:
    tunnel = Tunnel()
    assert tunnel.service == "ngrok"
    assert not tunnel.exposed
