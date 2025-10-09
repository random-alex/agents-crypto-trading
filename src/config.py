from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    # Agent's models set up
    MODEL_VERSION_NEWS_AGENT: str = "anthropic:claude-3-7-sonnet-latest"

    # Credentials
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
