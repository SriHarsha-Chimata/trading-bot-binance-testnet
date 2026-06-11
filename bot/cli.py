from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from .client import BinanceClient, BinanceAPIError
from .logging_config import setup_logging
from .orders import (
    place_limit_order,
    place_market_order,
    place_stop_limit_order,
    format_order_response,
)
from .validators import (
    ValidationError,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

load_dotenv()
logger = setup_logging()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Binance Futures Testnet — simplified trading bot",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="BUY or SELL")
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_LIMIT"],
        help="Order type",
    )
    parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    parser.add_argument("--price", type=float, default=None, help="Limit price (required for LIMIT / STOP_LIMIT)")
    parser.add_argument("--stop-price", type=float, default=None, help="Stop trigger price (required for STOP_LIMIT)")
    parser.add_argument(
        "--tif",
        default="GTC",
        choices=["GTC", "IOC", "FOK"],
        help="Time in force for LIMIT orders (default: GTC)",
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level (default: INFO)")
    return parser


def print_request_summary(args: argparse.Namespace) -> None:
    print("\n" + "=" * 50)
    print("  ORDER REQUEST SUMMARY")
    print("=" * 50)
    print(f"  Symbol     : {args.symbol}")
    print(f"  Side       : {args.side}")
    print(f"  Type       : {args.order_type}")
    print(f"  Quantity   : {args.quantity}")
    if args.price:
        print(f"  Price      : {args.price}")
    if args.stop_price:
        print(f"  Stop Price : {args.stop_price}")
    print("=" * 50)


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Re-init logger with requested level
    setup_logging(args.log_level)

    # --- Validate inputs ---
    try:
        args.symbol = validate_symbol(args.symbol)
        args.side = validate_side(args.side)
        args.order_type = validate_order_type(args.order_type)
        args.quantity = validate_quantity(args.quantity)
        args.price = validate_price(args.price, args.order_type)
        args.stop_price = validate_stop_price(args.stop_price, args.order_type)
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"\n[ERROR] {exc}")
        sys.exit(1)

    print_request_summary(args)

    # --- Load credentials ---
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")

    if not api_key or not api_secret:
        msg = "BINANCE_API_KEY and BINANCE_API_SECRET must be set in .env or environment."
        logger.error(msg)
        print(f"\n[ERROR] {msg}")
        sys.exit(1)

    # --- Place order ---
    try:
        with BinanceClient(api_key, api_secret) as client:
            if args.order_type == "MARKET":
                response = place_market_order(client, args.symbol, args.side, args.quantity)
            elif args.order_type == "LIMIT":
                response = place_limit_order(
                    client, args.symbol, args.side, args.quantity, args.price, args.tif
                )
            else:  # STOP_LIMIT
                response = place_stop_limit_order(
                    client, args.symbol, args.side, args.quantity, args.price, args.stop_price, args.tif
                )

        print(format_order_response(response))
        print("\n✅  Order placed successfully!\n")
        logger.info("Session complete — order placed successfully.")

    except BinanceAPIError as exc:
        print(f"\n❌  API Error [{exc.code}]: {exc.message}\n")
        logger.error("Order session ended with API error: %s", exc)
        sys.exit(1)
    except Exception as exc:
        print(f"\n❌  Unexpected error: {exc}\n")
        logger.exception("Order session ended with unexpected error")
        sys.exit(1)


if __name__ == "__main__":
    main()
