"""
BrainTrader
------------------------
Risk Management Engine (Phase 7)

Enforces strict institutional risk rules:
1. Volatility-Based Position Sizing (Max Risk % per trade).
2. Portfolio Exposure Limits (Max total capital deployed).
"""

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class RiskManager:
    def __init__(self, max_risk_per_trade_pct=0.02, max_portfolio_exposure_pct=0.60):
        """
        max_risk_per_trade_pct: Max % of total account balance to LOSE on a single trade (Default: 2%).
        max_portfolio_exposure_pct: Max % of total capital that can be actively in trades (Default: 60%).
        """
        self.max_risk_pct = max_risk_per_trade_pct
        self.max_exposure_pct = max_portfolio_exposure_pct

    def calculate_position_size(self, account_balance, current_deployed_capital, entry_price, stop_loss):
        """
        Calculates the exact number of shares to buy so that if the stop loss is hit,
        the account only loses a maximum of 2% of its total value.
        """
        if entry_price <= stop_loss:
            logging.warning("Risk Manager Reject: Stop loss is above or equal to entry price.")
            return 0, "Invalid Stop Loss"

        # 1. Check Portfolio Exposure Limits
        available_capital = account_balance - current_deployed_capital
        max_allowed_deployment = account_balance * self.max_exposure_pct

        if current_deployed_capital >= max_allowed_deployment:
            logging.warning("Risk Manager Reject: Maximum portfolio exposure reached. Halting new positions.")
            return 0, "Exposure Limit Reached"

        # 2. Calculate Risk Per Share (Distance to Stop Loss)
        risk_per_share = entry_price - stop_loss
        if risk_per_share <= 0:
            return 0, "Zero Risk Error"

        # 3. Calculate Total Allowed Risk in Rupees (e.g., 2% of ₹10,00,000 = ₹20,000 max loss)
        max_risk_amount = account_balance * self.max_risk_pct

        # 4. Calculate Number of Shares
        qty = int(max_risk_amount / risk_per_share)

        # 5. Capital Constraint Check
        total_cost = qty * entry_price
        
        # If the calculated size costs more than our remaining cash, reduce it
        if total_cost > available_capital:
            qty = int(available_capital / entry_price)

        if qty == 0:
            return 0, "Insufficient Capital for minimum 1 share"

        total_capital_at_risk = qty * risk_per_share
        
        return qty, {
            "shares": qty,
            "capital_required": round(qty * entry_price, 2),
            "max_loss_if_stopped": round(total_capital_at_risk, 2),
            "portfolio_risk_pct": round((total_capital_at_risk / account_balance) * 100, 2)
        }