from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import httpx

from .logging_config import setup_logging

BASE_URL = "https://testnet.binancefuture.com"

logger = setup_logging()


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceClient:
    """Thin wrapper around the Binance Futures Testnet REST API."""

    def __init__(self, api_key: str, api_secret: str, timeout: float = 10.0):
        self.api_key = api_key
        self.api_secret = api_secret
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={
                "X-MBX-APIKEY": api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> dict:
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _post(self, endpoint: str, params: dict) -> dict[str, Any]:
        params["timestamp"] = int(time.time() * 1000)
        params = self._sign(params)

        logger.debug("POST %s | params: %s", endpoint, {k: v for k, v in params.items() if k != "signature"})

        try:
            response = self._client.post(endpoint, data=params)
        except httpx.TimeoutException as exc:
            logger.error("Request timed out for %s: %s", endpoint, exc)
            raise
        except httpx.NetworkError as exc:
            logger.error("Network error for %s: %s", endpoint, exc)
            raise

        logger.debug("Response %s | status=%s | body=%s", endpoint, response.status_code, response.text)

        data = response.json()
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceAPIError(data["code"], data.get("msg", "Unknown error"))

        return data

    def _get(self, endpoint: str, params: dict | None = None) -> dict[str, Any]:
        params = params or {}
        params["timestamp"] = int(time.time() * 1000)
        params = self._sign(params)

        logger.debug("GET %s | params: %s", endpoint, {k: v for k, v in params.items() if k != "signature"})

        try:
            response = self._client.get(endpoint, params=params)
        except httpx.TimeoutException as exc:
            logger.error("Request timed out for %s: %s", endpoint, exc)
            raise
        except httpx.NetworkError as exc:
            logger.error("Network error for %s: %s", endpoint, exc)
            raise

        logger.debug("Response %s | status=%s | body=%s", endpoint, response.status_code, response.text)

        data = response.json()
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceAPIError(data["code"], data.get("msg", "Unknown error"))

        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def new_order(self, **kwargs) -> dict[str, Any]:
        """Place a new futures order."""
        return self._post("/fapi/v1/order", kwargs)

    def get_order(self, symbol: str, order_id: int) -> dict[str, Any]:
        """Query an existing order by ID."""
        return self._get("/fapi/v1/order", {"symbol": symbol, "orderId": order_id})

    def cancel_order(self, symbol: str, order_id: int) -> dict[str, Any]:
        """Cancel an open order."""
        return self._post("/fapi/v1/order", {"symbol": symbol, "orderId": order_id})

    def get_account(self) -> dict[str, Any]:
        """Fetch account information."""
        return self._get("/fapi/v2/account")

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
