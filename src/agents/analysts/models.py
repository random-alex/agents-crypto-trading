from pydantic import BaseModel
from typing import Literal
from pathlib import Path


class TechOutput(BaseModel):
    key_signals: list[str]
    decision: Literal["LONG", "SHORT", "NO_TRADE"]
    confidence: float
    entry: float
    stop_loss: float
    take_profit: list[float]
    risk_reward_ratio: str
    timeframe_alignment: bool

    def to_readable_string(self) -> str:
        """Convert to human-readable string format"""
        return f"""
    Decision: {self.decision}
    Confidence: {self.confidence}

    REASONING:
    {"*".join(self.key_signals)}


    SIGNAL:
    Entry: ${self.entry}
    Take Profit 1: ${self.take_profit}
    Stop Loss: ${self.stop_loss}
    Risk/Reward: {self.risk_reward_ratio}"""


class AgentsDeps(BaseModel):
    df_candle_path: Path
