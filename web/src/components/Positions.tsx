import { useState } from 'react';
import { api, type Position, type Status } from '../lib/api';
import { coin, market, price, r as fmtR, time, tone, usd } from '../lib/format';
import { useBotActions } from './Bots';
import { Btn, Coin, Dialog, Empty, SideTag } from './ui';

export function Positions({ status, refresh, onOpen }: { status: Status; refresh: () => void; onOpen: (p: Position) => void }) {
  const { busy, run } = useBotActions(refresh);
  const [confirm, setConfirm] = useState<Position | null>(null);
  const ps = status.positions;
  return (
    <section className="panel" aria-labelledby="pos-h">
      <div className="panel-head">
        <div>
          <h3 id="pos-h">Open positions</h3>
          <div className="sub">{ps.length ? `Valued at the live demo price${status.prices_ok ? '' : ' (prices unavailable right now)'}` : 'Nothing open right now'}</div>
        </div>
      </div>
      {ps.length === 0 ? (
        <Empty icon="inventory_2" title="No open positions">
          When a strategy's conditions all hold on a closed candle, its trade shows up here with its stop and live P&L.
        </Empty>
      ) : (
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Market</th><th>Side</th><th className="r">Size</th><th className="r">Entry</th><th className="r">Price</th>
                <th className="r">Stop</th><th className="r">P&amp;L</th><th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {ps.map(p => (
                <tr key={p.bot + p.symbol} className="clickable" onClick={() => onOpen(p)}>
                  <td>
                    <div className="sym"><Coin symbol={p.symbol} />
                      <div><div className="name">{coin(p.symbol)}</div><div className="meta">{market(p.symbol)} · {p.timeframe} · opened {time(p.entry_time || p.opened)}</div></div>
                    </div>
                  </td>
                  <td><SideTag side={p.side} />{p.leverage > 1 && <div className="t-small faint num">{p.leverage}× isolated</div>}</td>
                  <td className="r num">{p.size.toLocaleString('en-US', { maximumFractionDigits: 6 })}<div className="t-small faint">{usd(p.size * p.entry)}</div></td>
                  <td className="r num">{price(p.entry)}</td>
                  <td className="r num">{price(p.price)}</td>
                  <td className="r num">{price(p.stop)}<div className="t-small faint">risk {usd(p.risk_usd)}</div></td>
                  <td className={`r num ${tone(p.unrealized)}`}>
                    <b style={{ fontWeight: 500 }}>{usd(p.unrealized, true)}</b><div className="t-small">{fmtR(p.r_now)}</div>
                  </td>
                  <td className="r" onClick={e => e.stopPropagation()}>
                    <Btn kind="outlined" small busy={busy === p.symbol || p.close_pending} disabled={!status.bots[p.bot].running}
                      title={status.bots[p.bot].running ? 'Market-close this position' : 'Start the bot to close from here'}
                      onClick={() => setConfirm(p)}>Close</Btn>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Dialog
        open={!!confirm}
        onClose={() => setConfirm(null)}
        icon="close"
        title={confirm ? `Close ${coin(confirm.symbol)} ${confirm.side}?` : ''}
        actions={<>
          <Btn kind="text" onClick={() => setConfirm(null)}>Keep it</Btn>
          <Btn kind="danger" onClick={() => {
            const p = confirm!;
            setConfirm(null);
            run(p.symbol, () => api.closePosition(p.bot, p.symbol));
          }}>Close at market</Btn>
        </>}
      >
        {confirm && (
          <>
            <p>The {confirm.bot} bot sells at market on the demo account and cancels the resting stop.</p>
            <ul className="num">
              <li>Now about {usd(confirm.unrealized, true)} ({fmtR(confirm.r_now)})</li>
              <li>The strategy won't re-enter until its next signal.</li>
            </ul>
          </>
        )}
      </Dialog>
    </section>
  );
}
