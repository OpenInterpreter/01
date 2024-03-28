"""
Loads environment variables and creates a global configuration object.
"""

from dotenv import load_dotenv

from source.core.config import Config, get_config

load_dotenv()

config: Config = get_config()
