"""Read-only check that the futures bot can trade on YOUR OKX demo account.

    python check_futures.py

Checks account mode, position mode, the swap market, your swap fees and what a
typical entry would look like with the current strategy. Places no orders and
changes no settings.
"""
from __future__ import annotations

import sys

from config import Config
from check_connection import explain, fail, ok
from bot.futures import futures_cfg, plan
from bot.futures_runner import load_futures_strategy
from bot.strategies import signals_ls, warmup_bars


def main() -> None:
    cfg, spec = load_futures_strategy(futures_cfg(Config()))
    print("\n  OKX futures check (read-only, places no orders)\n")
    print(f"  host      {cfg.okx_hostname}")
    print(f"  mode      {'DEMO (simulated)' if cfg.demo else 'LIVE -- REAL MONEY'}")
    print(f"  market    {cfg.symbol} {cfg.timeframe}, isolated margin")
    print(f"  strategy  {spec.label()}")
    print(f"  risk      {cfg.fut_risk_fraction:.1%} of equity per trade, leverage <= "
          f"{cfg.fut_max_leverage}x, margin <= {cfg.fut_max_margin_fraction:.0%} of equity\n")
    if not cfg.demo:
        fail("DEMO=false. Futures run on demo only.")

    from bot.futures_exchange import OkxFutures
    try:
        ex = OkxFutures(cfg)
    except SystemExit:
        raise
    except Exception as e:
        fail("could not load markets: " + explain(e))
    ok(f"{ex.inst_id} found: {ex.contract_size:g} {ex.base} per contract, min {ex.min_contracts:g}")

    try:
        good, msg = ex.account_mode_ok()
    except Exception as e:
        fail("sign-in failed: " + explain(e))
    if not good:
        fail(msg)
    ok(msg)

    try:
        r = ex.client.privateGetAccountMaxSize({"instId": ex.inst_id, "tdMode": "isolated"})
        ok(f"futures trading allowed (max size now: {r['data'][0].get('maxBuy')} contracts)")
    except Exception as e:
        fail("futures not available on this key/account: " + explain(e) +
             "\n         In OKX > API, edit the key: Markets must include 'Perpetual'.")

    equity = ex.equity_quote()
    ok(f"equity {equity:,.2f} {ex.quote}")
    try:
        fee = ex.client.fetch_trading_fee(cfg.symbol)
        ok(f"swap fees: maker {float(fee['maker']):.3%}, taker {float(fee['taker']):.3%}  "
           f"(research assumes {cfg.fut_maker_fee:.3%} / {cfg.fut_taker_fee:.3%})")
    except Exception as e:
        print(f"  [warn] couldn't read swap fees ({explain(e)})")

    live = ex.position()
    if live:
        print(f"  [warn] an open {cfg.symbol} position exists ({live['size']} {ex.base}); the bot won't "
              "trade until it's closed")
    if ex.pending_protection():
        print("  [warn] stop/take-profit orders are already pending on this symbol")

    sig = signals_ls(ex.fetch_closed_ohlcv(warmup_bars(spec)), spec)
    bar = sig.iloc[-1]
    price, dist = float(bar["close"]), spec.stop_atr * float(bar["atr"])
    p = plan(equity, price, dist, 1, cfg)
    contracts = ex.to_contracts(p.size)
    ok(f"a trade right now would be: {contracts:g} contracts ({ex.to_base(contracts):.4f} {ex.base}, "
       f"~{p.notional:,.0f} {ex.quote}), {p.leverage}x, margin ~{p.margin:,.0f} {ex.quote}, "
       f"stop {dist / price:.2%} away, liquidation ~{abs(price - p.liq_price) / price:.1%} away, "
       f"risk ~{ex.to_base(contracts) * dist:,.0f} {ex.quote}")

    print("\n  All checks passed. No orders were placed.")
    print("  Start the futures bot with:  python -m bot.futures_runner\n")


if __name__ == "__main__":
    sys.exit(main())
