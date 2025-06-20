import time, hmac, hashlib, base64, requests, json
from src.core.config import settings


class MobeeOpenApi:
    BASE_URL = settings.MOBEE_OPEN_API_URL

    def __init__(self, API_KEY: str, API_SECRET: str):
        """
        Initialize the MobeeOpenApi client with a secret key.
        """
        self.API_KEY = API_KEY
        self.API_SECRET = API_SECRET

    def generate_signature(
        self, method: str, path: str, timestamp: str, body: str = None
    ):
        """
        Generate the X-Request-Signature header value.
        """
        str_to_sign = f"{method}\n{path}\n{timestamp}"
        if method in ["POST", "PUT"] and body:
            str_to_sign += f"\n{body}"

        digest = hmac.new(
            self.API_SECRET.encode("utf-8"), str_to_sign.encode("utf-8"), hashlib.sha256
        ).digest()
        return base64.b64encode(digest).decode()

    def get_auth_headers(self, method: str, path: str, body: str = None):
        """
        Construct authentication headers for a request.
        """
        timestamp = str(int(time.time()))
        signature = self.generate_signature(method, path, timestamp, body)

        headers = {
            "X-API-KEY": self.API_KEY,
            "X-Request-Signature": signature,
            "X-Request-Timestamp": timestamp,
            "Content-Type": "application/json",
        }

        return headers

    ## Wallets
    def get_balance(self, currency: str):
        """
        Get the balance of a specific currency.
        """
        method = "GET"
        endpoint = "/v1/wallets/balances"
        params = {"currency": currency}
        res = requests.get(
            f"{self.BASE_URL}{endpoint}",
            headers=self.get_auth_headers(method, endpoint),
            params=params,
        )
        if res.status_code == 200:
            return res.json()
        else:
            res.raise_for_status()

    ## Orders
    def create_new_order(
        self, side: str, market: str, trade: str, type: str, volume: float
    ):
        """
        Create a new order.
        """
        method = "POST"
        endpoint = "/v1/orders"
        body = {
            "side": side,
            "market": market,
            "trade": trade,
            "type": type,
            "volume": volume,
        }

        res = requests.post(
            f"{self.BASE_URL}{endpoint}",
            headers=self.get_auth_headers(method, endpoint, body=json.dumps(body)),
            json=body,
        )
        return res
