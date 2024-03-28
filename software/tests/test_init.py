from unittest.mock import patch

from source import Config, config


def test_config_loaded() -> None:
    with patch("source.core.config.get_config") as mock_get_config:
        mock_config: Config = config
        mock_get_config.return_value = mock_config
        from source import config as loaded_config  # pylint: disable=W0404,C0415

        assert loaded_config is mock_config
