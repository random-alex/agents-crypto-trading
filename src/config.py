from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    # Agent's models set up
    MODEL_VERSION_NEWS_AGENT: str = "anthropic:claude-sonnet-4-5"
    MODEL_VERSION_TECHANAL_AGENT: str = "anthropic:claude-sonnet-4-5"

    # Exchanges set up
    EXCHANGES: list[str] = ["Binance"]
    COINS: list[str] = ["BTCUSDT"]
    SAMPLING_FREQ: str = "15Min"  # freq of the graph

    # Credentials
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_DEMO_API_KEY", "")
    COINGECKO_ENVIRONMENT: str = os.getenv("COINGECKO_ENVIRONMENT", "demo")
    TIINGO_API_KEY: str = os.getenv("TIINGO_API_KEY", "")
