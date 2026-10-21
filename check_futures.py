"""Read-only check that the futures bot can trade on YOUR OKX demo account.

    python check_futures.py

Checks account mode, position mode, each strategy's swap market, your swap fees
and what an entry would look like right now. Places no orders and changes no
settings.
"""
from __future__ import annotations

import sys

from config import Config
from check_connection import explain, fail, ok
from bot.futures import futures_cfg, plan
from bot.futures_runner import load_futures_strategies
from bot.strategies import signals_ls, warmup_bars


def main() -> None:
    base = futures_cfg(Config())
    strategies = load_futures_strategies(base)
    print("\n  OKX futures check (read-only, places no orders)\n")
    print(f"  host      {base.okx_hostname}")
    print(f"  mode      {'DEMO (simulated)' if base.demo else 'LIVE -- REAL MONEY'}")
    print(f"  risk      {base.fut_risk_fraction:.1%} of equity per trade, leverage <= "
          f"{base.fut_max_leverage}x, margin <= {base.fut_max_margin_fraction:.0%} of equity "
          "(all positions together), isolated")
    for cfg, spec in strategies:
        print(f"  strategy  {cfg.symbol} {cfg.timeframe}: {spec.label()}")
    print()
    if not base.demo:
        fail("DEMO=false. Futures run on demo only.")

    from bot.futures_exchange import OkxFutures
    first = True
    for cfg, spec in strategies:
        try:
            ex = OkxFutures(cfg)
        except SystemExit:
            raise
        except Exception as e:
            fail("could not load markets: " + explain(e))
        ok(f"{ex.inst_id}: {ex.contract_size:g} {ex.base} per contract, min {ex.min_contracts:g}")

        if first:
            try:
                good, msg = ex.account_mode_ok()
            except Exception as e:
                fail("sign-in failed: " + explain(e))
            if not good:
                fail(msg)
            ok(msg)
            equity = ex.equity_quote()
            ok(f"equity {equity:,.2f} {ex.quote}")
            try:
                fee = ex.client.fetch_trading_fee(cfg.symbol)
                ok(f"swap fees: maker {float(fee['maker']):.3%}, taker {float(fee['taker']):.3%}  "
                   f"(research assumes {cfg.fut_maker_fee:.3%} / {cfg.fut_taker_fee:.3%})")
            except Exception as e:
                print(f"  [warn] couldn't read swap fees ({explain(e)})")
            first = False

        try:
            r = ex.client.privateGetAccountMaxSize({"instId": ex.inst_id, "tdMode": "isolated"})
            ok(f"{ex.inst_id} futures trading allowed (max now: {r['data'][0].get('maxBuy')} contracts)")
        except Exception as e:
            fail(f"{ex.inst_id} not tradable with this key/account: " + explain(e) +
                 "\n         In OKX > API, edit the key: Markets must include 'Perpetual'.")

        live = ex.position()
        if live:
            print(f"  [warn] an open {cfg.symbol} position exists; the bot won't trade it")
        sig = signals_ls(ex.fetch_closed_ohlcv(warmup_bars(spec)), spec)
        bar = sig.iloc[-1]
        price, dist = float(bar["close"]), spec.stop_atr * float(bar["atr"])
        p = plan(equity, price, dist, 1, cfg)
        contracts = ex.to_contracts(p.size)
        ok(f"{ex.base} trade right now: {contracts:g} contracts ({ex.to_base(contracts):.4f} {ex.base}, "
           f"~{p.notional:,.0f} {ex.quote}), {p.leverage}x, margin ~{p.margin:,.0f}, stop "
           f"{dist / price:.2%} away, liquidation ~{abs(price - p.liq_price) / price:.1%} away, "
           f"risk ~{ex.to_base(contracts) * dist:,.0f} {ex.quote}")

    print("\n  All checks passed. No orders were placed.")
    print("  Start the futures bot with:  python -m bot.futures_runner\n")


if __name__ == "__main__":
    sys.exit(main())
