"""Read-only check that the bot can reach YOUR OKX demo account.

    python check_connection.py

It loads .env, signs in with your demo API key, and reports: API host, demo
mode, key permissions, balances, the market's minimum order size and whether
your risk settings produce an order above it. It never places, changes or
cancels an order.
"""
from __future__ import annotations

import sys

from config import Config
from bot.runner import load_strategy

HINTS = {
    "50101": "This key belongs to the other environment. Demo keys must be created while OKX is "
             "in Demo Trading mode, and need DEMO=true (and live keys DEMO=false).",
    "50102": "Timestamp rejected: your PC clock is off. Sync it (Windows: Settings > Time > Sync now).",
    "50103": "OKX_API_KEY is missing or malformed in .env.",
    "50105": "OKX_API_PASSPHRASE is wrong: it's the passphrase you typed when creating the key, "
             "not your login password.",
    "50110": "Your IP isn't on this key's IP allowlist. Add your current IP in OKX, or remove the allowlist.",
    "50111": "OKX_API_KEY is not recognised. Check for typos or spaces in .env.",
    "50113": "Signature invalid: OKX_API_SECRET is wrong.",
    "50119": "OKX doesn't know this key on OKX_HOSTNAME. Check it was copied from the API page; "
             "if it was, your account is on another OKX site: set OKX_HOSTNAME to the one you "
             "log in on (app.okx.com global, my.okx.com EEA, tr.okx.com Turkey, us.okx.com US).",
}


def explain(exc: Exception) -> str:
    text = str(exc)
    for code, hint in HINTS.items():
        if code in text:
            return f"OKX error {code}: {hint}"
    if "timed out" in text or "SSL" in text or "NetworkError" in type(exc).__name__:
        return ("Network problem reaching OKX. If www.okx.com is blocked on your network, set "
                "OKX_HOSTNAME=app.okx.com in .env.")
    return text


def ok(msg):
    print(f"  [ok]   {msg}")


def fail(msg):
    print(f"  [FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    cfg, spec = load_strategy(Config())
    print(f"\n  OKX connection check (read-only, places no orders)\n")
    print(f"  host      {cfg.okx_hostname}")
    print(f"  mode      {'DEMO (simulated)' if cfg.demo else 'LIVE -- REAL MONEY'}")
    print(f"  market    {cfg.symbol} {cfg.timeframe}")
    print(f"  strategy  {spec.label()}")
    orders = "maker first (post-only limit), market fallback" if cfg.execution == "maker" else "market"
    print(f"  orders    {orders}\n")
    if not cfg.demo:
        fail("DEMO=false. Phase 1 is demo only; set DEMO=true in .env.")

    missing = [n for n, v in (("OKX_API_KEY", cfg.api_key), ("OKX_API_SECRET", cfg.api_secret),
                              ("OKX_API_PASSPHRASE", cfg.api_passphrase)) if not v]
    if missing:
        fail("missing in .env: " + ", ".join(missing))
    ok(".env has all three credentials")

    from bot.exchange import OkxExchange
    try:
        ex = OkxExchange(cfg)
    except SystemExit:
        raise
    except Exception as e:
        fail("could not load markets: " + explain(e))
    ok(f"reached OKX, {cfg.symbol} spot market found")

    try:
        acct = ex.client.privateGetAccountConfig()["data"][0]
    except Exception as e:
        fail("sign-in failed: " + explain(e))
    perms = acct.get("perm", "")
    ok(f"signed in to the demo account (account level {acct.get('acctLv')}, permissions: {perms})")
    if "trade" not in perms:
        fail("this key has no Trade permission. Edit the key in OKX and enable Trade.")
    if "withdraw" in perms:
        print("  [warn] this key can WITHDRAW. The bot never needs that; create a key without it.")

    try:
        bal = ex.client.fetch_balance()
    except Exception as e:
        fail("balance read failed: " + explain(e))
    quote = float(bal.get(ex.quote, {}).get("free") or 0)
    base = float(bal.get(ex.base, {}).get("free") or 0)
    ok(f"balances: {quote:,.2f} {ex.quote} free, {base:.8f} {ex.base} free")
    if base > 0:
        print(f"         (the bot ignores the {ex.base} you already hold; it only sells what it buys)")

    try:
        fee = ex.trading_fee()
        ok(f"your fee rate on {cfg.symbol}: maker {fee['maker']:.3%}, taker {fee['taker']:.3%}"
           f"  (.env assumes maker {cfg.maker_fee:.3%}, taker {cfg.taker_fee:.3%})")
        if abs(fee["maker"] - cfg.maker_fee) > 1e-6 or abs(fee["taker"] - cfg.taker_fee) > 1e-6:
            print(f"         set MAKER_FEE={fee['maker']:g} and TAKER_FEE={fee['taker']:g} in .env, "
                  "then re-run research.py so it uses your real costs")
    except Exception as e:
        print(f"  [warn] couldn't read your fee rate ({explain(e)}); research uses the .env values")

    price = ex.last_price()
    min_amt = ex.min_amount()
    order_amt = cfg.max_notional_usd / price
    ok(f"last price {price:,.2f}; minimum order {min_amt} {ex.base} (~{min_amt * price:,.2f} {ex.quote})")
    if order_amt < min_amt:
        fail(f"MAX_NOTIONAL_USD={cfg.max_notional_usd} buys {order_amt:.8f} {ex.base}, below the "
             f"minimum. Raise MAX_NOTIONAL_USD.")
    if quote < cfg.max_notional_usd:
        fail(f"only {quote:.2f} {ex.quote} free; the bot needs at least MAX_NOTIONAL_USD="
             f"{cfg.max_notional_usd}. Top up the demo account in OKX.")
    ok(f"a full-size entry would be up to {order_amt:.8f} {ex.base} (~{cfg.max_notional_usd} {ex.quote})")

    print("\n  All checks passed. No orders were placed.")
    print("  Start the bot with:  python -m bot.runner\n")


if __name__ == "__main__":
    main()
