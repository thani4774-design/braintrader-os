"""
BrainTrader
------------------------
Historical Multi-Timeframe Backtest

Backtests MTF structure plus indicator confirmation using only information
available at each historical signal date.
"""

from pathlib import Path

import pandas as pd

from historical_mtf_engine import analyze_historical_mtf
from indicator_confirmation import indicator_confirmation
from indicators import calculate_indicators
from recommendation_engine import create_recommendation


def run_historical_mtf_backtest(
    df,
    starting_capital=100000,
    risk_percent=1,
    max_holding_days=10,
    evaluation_interval_days=5,
    trade_log_path="Historical_MTF_Backtest_Trades.csv",
    start_date=None,
    end_date=None,
):
    """Backtest the complete MTF and indicator-confirmation strategy.

    Signals are calculated at each weekly evaluation close and are entered at
    the next day's open. No future candles are included in either the MTF or
    indicator analysis.
    """
    required_columns = {"Date", "Open", "High", "Low", "Close", "Volume"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    data = df.copy()
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.sort_values("Date").reset_index(drop=True)

    for column in ["Open", "High", "Low", "Close", "Volume"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["Open", "High", "Low", "Close"]).reset_index(drop=True)
    data = calculate_indicators(data)

    first_signal_date = data["Date"].iloc[0] + pd.DateOffset(years=15)
    evaluation_start_date = first_signal_date
    evaluation_end_date = data["Date"].iloc[-1]

    if start_date is not None:
        evaluation_start_date = max(
            evaluation_start_date,
            pd.Timestamp(start_date),
        )

    if end_date is not None:
        evaluation_end_date = min(
            evaluation_end_date,
            pd.Timestamp(end_date),
        )

    signal_index = int(data["Date"].searchsorted(evaluation_start_date))
    end_index = int(data["Date"].searchsorted(evaluation_end_date, side="right")) - 1

    capital = float(starting_capital)
    brokerage_rate = 0.0003
    slippage_rate = 0.0005
    total_trades = 0
    wins = 0
    losses = 0
    gross_profit = 0.0
    gross_loss = 0.0
    equity_curve = [capital]
    peak_equity = capital
    max_drawdown = 0.0
    trade_log = []

    while signal_index < end_index:
        latest = data.iloc[signal_index]

        if pd.isna(latest["ATR"]) or latest["ATR"] <= 0:
            signal_index += evaluation_interval_days
            continue

        mtf = analyze_historical_mtf(data.iloc[: signal_index + 1], latest["Date"])
        if mtf is None:
            signal_index += evaluation_interval_days
            continue

        indicator = indicator_confirmation(data.iloc[: signal_index + 1])
        entry_index = signal_index + 1
        entry_price = float(data["Open"].iloc[entry_index])

        recommendation = create_recommendation(
            stock="HISTORICAL",
            price=entry_price,
            mtf_score=mtf["mtf_score"],
            alignment=mtf["alignment"]["alignment"],
            indicator_score=indicator["score"],
            atr=float(latest["ATR"]),
            reasons=mtf["reasons"],
        )

        if recommendation["Decision"] not in {"STRONG_BUY", "BUY_WATCH"}:
            signal_index += evaluation_interval_days
            continue

        stop_loss = recommendation["Stop Loss"]
        target = recommendation["Target"]
        risk_per_share = entry_price - stop_loss

        if risk_per_share <= 0 or entry_price <= 0:
            signal_index += evaluation_interval_days
            continue

        risk_amount = capital * (risk_percent / 100)
        quantity = min(
            int(risk_amount / risk_per_share),
            int(capital / entry_price),
        )

        if quantity <= 0:
            signal_index += evaluation_interval_days
            continue

        exit_index = min(entry_index + max_holding_days - 1, end_index)
        exit_price = float(data["Close"].iloc[exit_index])

        # Stop is prioritized if a daily candle reaches both levels.
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

        trade_value = quantity * entry_price
        exit_value = quantity * exit_price
        gross_pnl = (exit_price - entry_price) * quantity
        costs = (trade_value + exit_value) * (brokerage_rate + slippage_rate)
        net_profit = gross_pnl - costs
        net_profit_percent = (net_profit / trade_value) * 100

        capital += net_profit
        total_trades += 1
        equity_curve.append(capital)
        peak_equity = max(peak_equity, capital)
        max_drawdown = max(
            max_drawdown,
            ((peak_equity - capital) / peak_equity) * 100,
        )

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
                "Entry Price": round(entry_price, 2),
                "Exit Price": round(exit_price, 2),
                "Stop Loss": round(stop_loss, 2),
                "Target": round(target, 2),
                "Quantity": quantity,
                "MTF Score": mtf["mtf_score"],
                "Indicator Score": indicator["score"],
                "Final Score": recommendation["Final Score"],
                "Profit %": round(net_profit_percent, 2),
                "Net Profit": round(net_profit, 2),
                "Capital": round(capital, 2),
            }
        )

        # Prevent overlapping positions while this trade is open.
        signal_index = exit_index + 1

    win_rate = (wins / total_trades * 100) if total_trades else 0
    average_profit = (
        sum(trade["Profit %"] for trade in trade_log) / total_trades
        if total_trades
        else 0
    )
    profit_factor = (gross_profit / gross_loss) if gross_loss else 0

    years = max(
        (data["Date"].iloc[end_index] - evaluation_start_date).days / 365.25,
        1 / 365.25,
    )
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
        "Evaluation Start": str(evaluation_start_date.date()),
        "Evaluation End": str(data["Date"].iloc[end_index].date()),
        "Equity Curve": equity_curve,
    }
