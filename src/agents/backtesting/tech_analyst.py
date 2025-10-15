from src.agents.analysts.technical_analyst import run_tech_analysis
from src.agents.utils.exchange_utils import get_coin_prices
from src.config import Config
from tqdm import tqdm
import random
from datetime import datetime
import pandas as pd
from pathlib import Path

random.seed(13)


def get_first_index_safely(indexes):
    return indexes[0] if len(indexes) > 0 else None


def run_test(test_name: str, num_tests: int = 1):
    """
    Func to run the testing of the new agentic system
    test_name - MUST BE UNIQUE!
    """
    start_date = datetime(2024, 1, 1, 0, 0, 0).timestamp()
    end_date = datetime(2025, 10, 1, 23, 59, 59).timestamp()
    test_results = []
    for i in tqdm(range(num_tests)):
        # Generate random timestamp
        random_timestamp = int(random.uniform(start_date, end_date) * 1000)
        file_id = datetime.fromtimestamp(random_timestamp / 1000).strftime(
            "%Y-%m-%d_%H:%M:%S"
        )

        parent_folder = Path(f"logs/backtest/{test_name}/raw_results/{file_id}")
        parent_folder.mkdir(parents=True, exist_ok=True)

        filepath = parent_folder / "1day.png"
        filepath_week = parent_folder / "1week.png"
        filepath_res = parent_folder / "raw_agent_prediction.json"

        res = run_tech_analysis(
            symbol=Config.COIN,
            start_date=random_timestamp - ((1000 * 60) * 60) * 24,
            end_date=random_timestamp,
            filepath=filepath,
            filepath_week=filepath_week,
        )
        df = get_coin_prices(
            start_date=random_timestamp,
            end_date=random_timestamp + ((1000 * 60) * 60) * 24 * 4,
        )
        timestamp_profit_1 = None
        timestamp_profit_2 = None
        timestamp_profit_3 = None
        timestamp_loss = None
        timpestamps_open = df.index[0]
        if res.decision == "SHORT":
            timestamp_profit_1 = get_first_index_safely(
                df.loc[df["low"] <= res.take_profit[0]].index
            )
            timestamp_profit_2 = get_first_index_safely(
                df.loc[df["low"] <= res.take_profit[1]].index
            )
            timestamp_profit_3 = get_first_index_safely(
                df.loc[df["low"] <= res.take_profit[2]].index
            )
            timestamp_loss = get_first_index_safely(
                df.loc[df["high"] >= res.stop_loss].index
            )
            trade_type = "short"
        elif res.decision == "LONG":
            timestamp_profit_1 = get_first_index_safely(
                df.loc[df["high"] >= res.take_profit[0]].index
            )
            timestamp_profit_2 = get_first_index_safely(
                df.loc[df["high"] >= res.take_profit[1]].index
            )
            timestamp_profit_3 = get_first_index_safely(
                df.loc[df["high"] >= res.take_profit[2]].index
            )
            timestamp_loss = get_first_index_safely(
                df.loc[df["low"] <= res.stop_loss].index
            )
            trade_type = "long"
        else:
            trade_type = "no-trade"

        test_results.append(
            {
                "timestamp_profit_1": timestamp_profit_1,
                "timestamp_profit_2": timestamp_profit_2,
                "timestamp_profit_3": timestamp_profit_3,
                "timestamp_loss": timestamp_loss,
                "trade_type": trade_type,
                "timpestamps_open": timpestamps_open,
                "open_price": float(
                    df[
                        [
                            "open",
                            "close",
                        ]
                    ]
                    .iloc[0]
                    .mean()
                ),
                "take_profit_1": res.take_profit[0],
                "take_profit_2": res.take_profit[1],
                "take_profit_3": res.take_profit[2],
                "stop_loss": res.stop_loss,
                "confidence": res.confidence,
                "risk_reward_ratio": res.risk_reward_ratio,
            }
        )
        with open(filepath_res, "w") as f:
            f.write(res.model_dump_json(indent=2))
    df_res = pd.DataFrame(test_results)
    df_res["profitable"] = df_res["timestamp_profit_1"] < df_res["timestamp_loss"]
    path_df_res = parent_folder.parent / "res.csv"
    df_res.loc[df_res["trade_type"] == "no-trade", "profitable"] = pd.NA
    df_res.to_csv(path_df_res)
    return df_res, path_df_res


def analyze_test(path: Path):
    df = pd.read_csv(path, index_col=0)
    df_open_trades = df.loc[df["trade_type"] != "no-trade"]
    print(df_open_trades["profitable"].sum() / df_open_trades.shape[0])


if __name__ == "__main__":
    res, path_saved = run_test(num_tests=30, test_name="ind_better_output")
    analyze_test(path_saved)
    print(res)
