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


class AgentsDeps(BaseModel):
    df_candle_path: Path
