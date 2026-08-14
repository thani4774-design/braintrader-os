import os
import pyotp
from dotenv import load_dotenv
from SmartApi import SmartConnect

# 1. Look for .env in both the root folder and Code folder
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_env = os.path.join(base_dir, ".env")
code_env = os.path.join(base_dir, "Code", ".env")

if os.path.exists(root_env):
    print(f"[DEBUG] Found .env at: {root_env}")
    load_dotenv(dotenv_path=root_env)
elif os.path.exists(code_env):
    print(f"[DEBUG] Found .env at: {code_env}")
    load_dotenv(dotenv_path=code_env)
else:
    print(f"[DEBUG] WARNING: Could not find .env file in {base_dir} or {os.path.join(base_dir, 'Code')}")

class AngelOneAPI:
    def __init__(self):
        self.api_key = os.getenv("ANGEL_API_KEY")
        self.client_id = os.getenv("ANGEL_CLIENT_ID")
        self.pin = os.getenv("ANGEL_PIN")
        self.totp_secret = os.getenv("ANGEL_TOTP_SECRET")
        
        # Diagnostic print to check loaded status (without printing secret values)
        print("\n--- Credential Check ---")
        print(f"ANGEL_API_KEY Loaded:     {'YES' if self.api_key else 'NO'}")
        print(f"ANGEL_CLIENT_ID Loaded:   {'YES' if self.client_id else 'NO'}")
        print(f"ANGEL_PIN Loaded:         {'YES' if self.pin else 'NO'}")
        print(f"ANGEL_TOTP_SECRET Loaded: {'YES' if self.totp_secret else 'NO'}")
        print("------------------------\n")

        if not all([self.api_key, self.client_id, self.pin, self.totp_secret]):
            raise ValueError("[ERROR] Missing credentials. Please verify variable names in your .env file.")
            
        self.smartApi = SmartConnect(api_key=self.api_key)
        self.auth_token = None

    def login(self):
        """Generates the live TOTP and authenticates the session."""
        try:
            current_totp = pyotp.TOTP(self.totp_secret).now()
            data = self.smartApi.generateSession(self.client_id, self.pin, current_totp)
            
            if data.get('status') == True:
                self.auth_token = data['data']['jwtToken']
                print(f"[SUCCESS] Secure connection established for Client ID: {self.client_id}")
                return True
            else:
                print(f"[FAILED] Angel One Login Error: {data.get('message')}")
                return False
                
        except Exception as e:
            print(f"[EXCEPTION] Connection Error: {e}")
            return False

    def get_available_balance(self):
        """Fetches the live available cash/margin from Angel One RMS Limits."""
        try:
            rms_data = self.smartApi.rmsLimit()
            if rms_data.get('status') == True and rms_data.get('data'):
                # 'net' represents total available trading margin
                net_balance = float(rms_data['data'].get('net', 0.0))
                available_cash = float(rms_data['data'].get('availablecash', 0.0))
                
                margin = net_balance if net_balance > 0 else available_cash
                print(f"[ANGEL ONE API] Live Available Capital: ₹{margin:,.2f}")
                return margin
            else:
                print(f"[WARNING] Could not read balance: {rms_data.get('message')}")
                return 0.0
        except Exception as e:
            print(f"[ERROR] Failed to fetch margin balance: {e}")
            return 0.0

if __name__ == "__main__":
    print("==================================================")
    print(" TESTING LIVE ANGEL ONE API CONNECTION ")
    print("==================================================")
    
    broker = AngelOneAPI()
    if broker.login():
        print("\n--- Testing Data Flow ---")
        balance = broker.get_available_balance()
        print(f"Returned Balance: ₹{balance:,.2f}")
        print("-------------------------\n")