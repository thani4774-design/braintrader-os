"""
BrainTrader
------------------------
Daily Indicator Strategy Backtest

Evaluates the indicator-confirmation and ATR risk-management rules without
using future prices to create an entry signal.
"""

from pathlib import Path

import pandas as pd

from indicator_confirmation import indicator_confirmation
from indicators import calculate_indicators


def run_backtest(
    df,
    starting_capital=100000,
    risk_percent=1,
    max_holding_days=10,
    minimum_indicator_score=70,
    trade_log_path="Backtest_Trades.csv",
):
    """Backtest the daily technical-confirmation strategy.

    A signal is calculated at the close of a day, then entered at the next
    day's open. Only one trade can be open at a time.
    """
    data = df.copy()

    required_columns = {"Date", "Open", "High", "Low", "Close", "Volume"}
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    for column in ["Open", "High", "Low", "Close", "Volume"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["Open", "High", "Low", "Close"]).reset_index(drop=True)
    data = calculate_indicators(data)

    capital = float(starting_capital)
    brokerage_rate = 0.0003
    slippage_rate = 0.0005
    total_trades = 0
    wins = 0
    losses = 0
    gross_profit = 0.0
    gross_loss = 0.0
    trade_log = []
    equity_curve = [capital]
    peak_equity = capital
    max_drawdown = 0.0

    # EMA200 and ADX require sufficient historical candles before signals can
    # be evaluated. The final window must leave room for a next-day entry.
    signal_index = 200

    while signal_index < len(data) - 1:
        current_df = data.iloc[: signal_index + 1]
        latest = current_df.iloc[-1]

        if pd.isna(latest["ATR"]) or latest["ATR"] <= 0:
            signal_index += 1
            continue

        indicator = indicator_confirmation(current_df)
        qualifies = (
            indicator["score"] >= minimum_indicator_score
            and latest["Close"] >= latest["EMA200"]
            and latest["ADX"] >= 20
        )

        if not qualifies:
            signal_index += 1
            continue

        entry_index = signal_index + 1
        entry = float(data["Open"].iloc[entry_index])
        atr = float(latest["ATR"])
        stop_loss = entry - atr
        target = entry + (2 * atr)
        risk_per_share = entry - stop_loss

        if risk_per_share <= 0 or entry <= 0:
            signal_index += 1
            continue

        risk_amount = capital * (risk_percent / 100)
        risk_quantity = int(risk_amount / risk_per_share)
        affordable_quantity = int(capital / entry)
        quantity = min(risk_quantity, affordable_quantity)

        if quantity <= 0:
            signal_index += 1
            continue

        exit_index = min(entry_index + max_holding_days - 1, len(data) - 1)
        exit_price = float(data["Close"].iloc[exit_index])

        # A stop is prioritized if both stop and target occur in one candle.
        for candle_index in range(entry_index, exit_index + 1):
            candle = data.iloc[candle_index]

            if float(candle["Low"]) <= stop_loss:
                exit_price = stop_loss
                exit_index = candle_index
                break

            if float(candle["High"]) >= target:
                exit_price = target
                exit_index = candle_index
                break

        trade_value = quantity * entry
        exit_value = quantity * exit_price
        gross_pnl = (exit_price - entry) * quantity
        brokerage = (trade_value + exit_value) * brokerage_rate
        slippage = (trade_value + exit_value) * slippage_rate
        net_profit = gross_pnl - brokerage - slippage
        net_profit_percent = (net_profit / trade_value) * 100

        capital += net_profit
        total_trades += 1
        equity_curve.append(capital)

        peak_equity = max(peak_equity, capital)
        drawdown = ((peak_equity - capital) / peak_equity) * 100
        max_drawdown = max(max_drawdown, drawdown)

        if net_profit > 0:
            wins += 1
            gross_profit += net_profit
        else:
            losses += 1
            gross_loss += abs(net_profit)

        trade_log.append(
            {
                "Entry Date": str(data["Date"].iloc[entry_index])[:10],
                "Exit Date": str(data["Date"].iloc[exit_index])[:10],
                "Entry Price": round(entry, 2),
                "Exit Price": round(exit_price, 2),
                "Stop Loss": round(stop_loss, 2),
                "Target": round(target, 2),
                "Quantity": quantity,
                "Indicator Score": indicator["score"],
                "ADX": round(float(latest["ADX"]), 2),
                "Profit %": round(net_profit_percent, 2),
                "Net Profit": round(net_profit, 2),
                "Capital": round(capital, 2),
            }
        )

        # Do not open overlapping positions while this trade is active.
        signal_index = exit_index + 1

    win_rate = (wins / total_trades * 100) if total_trades else 0
    average_profit = (
        sum(trade["Profit %"] for trade in trade_log) / total_trades
        if total_trades
        else 0
    )
    profit_factor = (gross_profit / gross_loss) if gross_loss else 0

    years = max(len(data) / 252, 1 / 252)
    cagr = ((capital / starting_capital) ** (1 / years) - 1) * 100

    if trade_log_path:
        pd.DataFrame(trade_log).to_csv(Path(trade_log_path), index=False)

    return {
        "Starting Capital": starting_capital,
        "Ending Capital": round(capital, 2),
        "Total Trades": total_trades,
        "Wins": wins,
        "Losses": losses,
        "Win Rate": round(win_rate, 2),
        "Net Profit %": round(((capital - starting_capital) / starting_capital) * 100, 2),
        "CAGR %": round(cagr, 2),
        "Average Profit %": round(average_profit, 2),
        "Profit Factor": round(profit_factor, 2),
        "Max Drawdown %": round(max_drawdown, 2),
        "Equity Curve": equity_curve,
    }
