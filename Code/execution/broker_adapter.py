"""
BrainTrader
------------------------
Execution Adapter (Phase 3)

An interface-based broker adapter. This decouples our Confluence logic
from specific broker APIs, allowing seamless switching between Paper Trading,
Zerodha, or Dhan.
"""

class BrokerAdapter:
    """Base interface that all broker connections must implement."""
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.is_connected = False

    def connect(self):
        raise NotImplementedError("Connect method must be overridden.")

    def get_account_balance(self):
        raise NotImplementedError("Must return available margin.")

    def place_order(self, symbol, order_type, quantity, price=None, stop_loss=None, target=None):
        """
        Submits the order.
        order_type: 'MARKET' or 'LIMIT'
        """
        raise NotImplementedError("Place order method must be overridden.")

class PaperTradingBroker(BrokerAdapter):
    """A simulated broker for forward-testing our algorithms."""
    def __init__(self, initial_balance=1000000): # 10 Lakh starting capital
        super().__init__()
        self.balance = initial_balance
        self.positions = {}
        self.is_connected = True
        print(f"[*] Paper Trading Initialized. Balance: ₹{self.balance}")

    def connect(self):
        return True

    def get_account_balance(self):
        return self.balance

    def place_order(self, symbol, order_type, quantity, price, stop_loss=None, target=None):
        """Simulates placing an order and tracks it in memory."""
        cost = quantity * price
        
        if cost > self.balance:
            print(f"[!] Order Rejected: Insufficient Margin for {symbol}")
            return False

        self.balance -= cost
        self.positions[symbol] = {
            "quantity": quantity,
            "entry_price": price,
            "stop_loss": stop_loss,
            "target": target
        }
        
        print(f"[+] PAPER TRADE EXECUTED: Bought {quantity} {symbol} @ ₹{price}")
        print(f"    -> Stop Loss: ₹{stop_loss} | Target: ₹{target}")
        print(f"    -> Remaining Margin: ₹{self.balance}")
        
        return True

# Future: class ZerodhaBroker(BrokerAdapter): ...
# Future: class DhanBroker(BrokerAdapter): ...