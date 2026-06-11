from __future__ import annotations

from typing import Any

from .client import BinanceClient, BinanceAPIError
from .logging_config import setup_logging

logger = setup_logging()


def place_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
) -> dict[str, Any]:
    """Place a MARKET order on Binance Futures Testnet."""
    logger.info(
        "Placing MARKET order | symbol=%s side=%s quantity=%s",
        symbol, side, quantity,
    )
    params = dict(symbol=symbol, side=side, type="MARKET", quantity=quantity)
    try:
        response = client.new_order(**params)
        logger.info("MARKET order placed successfully | orderId=%s status=%s", response.get("orderId"), response.get("status"))
        return response
    except BinanceAPIError as exc:
        logger.error("MARKET order failed | %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error placing MARKET order | %s", exc)
        raise


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> dict[str, Any]:
    """Place a LIMIT order on Binance Futures Testnet."""
    logger.info(
        "Placing LIMIT order | symbol=%s side=%s quantity=%s price=%s timeInForce=%s",
        symbol, side, quantity, price, time_in_force,
    )
    params = dict(
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce=time_in_force,
    )
    try:
        response = client.new_order(**params)
        logger.info("LIMIT order placed successfully | orderId=%s status=%s", response.get("orderId"), response.get("status"))
        return response
    except BinanceAPIError as exc:
        logger.error("LIMIT order failed | %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error placing LIMIT order | %s", exc)
        raise


def place_stop_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
    time_in_force: str = "GTC",
) -> dict[str, Any]:
    """Place a STOP_LIMIT order on Binance Futures Testnet (bonus)."""
    logger.info(
        "Placing STOP_LIMIT order | symbol=%s side=%s quantity=%s price=%s stopPrice=%s",
        symbol, side, quantity, price, stop_price,
    )
    params = dict(
        symbol=symbol,
        side=side,
        type="STOP",
        quantity=quantity,
        price=price,
        stopPrice=stop_price,
        timeInForce=time_in_force,
    )
    try:
        response = client.new_order(**params)
        logger.info("STOP_LIMIT order placed successfully | orderId=%s status=%s", response.get("orderId"), response.get("status"))
        return response
    except BinanceAPIError as exc:
        logger.error("STOP_LIMIT order failed | %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error placing STOP_LIMIT order | %s", exc)
        raise


def format_order_response(response: dict[str, Any]) -> str:
    """Return a human-readable summary of an order response."""
    lines = [
        "",
        "=" * 50,
        "  ORDER RESPONSE",
        "=" * 50,
        f"  Order ID     : {response.get('orderId', 'N/A')}",
        f"  Symbol       : {response.get('symbol', 'N/A')}",
        f"  Side         : {response.get('side', 'N/A')}",
        f"  Type         : {response.get('type', 'N/A')}",
        f"  Status       : {response.get('status', 'N/A')}",
        f"  Orig Qty     : {response.get('origQty', 'N/A')}",
        f"  Executed Qty : {response.get('executedQty', 'N/A')}",
        f"  Avg Price    : {response.get('avgPrice', 'N/A')}",
        f"  Price        : {response.get('price', 'N/A')}",
        f"  Time in Force: {response.get('timeInForce', 'N/A')}",
        "=" * 50,
    ]
    return "\n".join(lines)
