import { useEffect, useMemo, useState } from 'react';
import type { Trade } from '../lib/api';
import type { ConsoleData, Route } from '../lib/store';
import { coin, duration, market, price, reasonLabel, r as fmtR, strategyName, time, tone, usd } from '../lib/format';
import { PriceChart, type Level } from '../components/PriceChart';
import { Checklist } from '../components/Thinking';
import { useAnalysis } from './Strategies';
import { Btn, Chip, Coin, Empty, FilterChip, Icon, SideTag, Skeleton } from '../components/ui';

const EXIT_STORY: Record<string, string> = {
  stop: 'Price reached the stop-loss, so the bot closed the trade at market.',
  'exchange stop/tp': 'The stop resting on OKX was hit and OKX closed the position.',
  signal: "The strategy's exit rule fired on a closed candle.",
  tp: 'Price reached the take-profit target.',
  'trailing stop': 'The trade moved far enough in its favour for the stop to start trailing; price then came back to the trailed stop.',
  manual: 'You closed it from the console.',
  'daily target': 'The daily profit target was reached with "close open positions" switched on.'
};

type SortKey = 'exit_time' | 'pnl' | 'r' | 'symbol';

function TradeSheet({ trade, onClose }: { trade: Trade | null; onClose: () => void }) {
  const [open, setOpen] = useState(false);
  const [shown, setShown] = useState<Trade | null>(trade);
  useEffect(() => {
    if (trade) { setShown(trade); requestAnimationFrame(() => setOpen(true)); } else setOpen(false);
  }, [trade]);
  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [onClose]);
  const t = shown;
  const { a, err } = useAnalysis(t?.bot, t?.symbol, t?.id);
  const levels = useMemo<Level[]>(() => {
    if (!t) return [];
    const l: Level[] = [{ price: t.entry, label: 'Entry', tone: 'primary', dashed: false }];
    if (t.stop) l.push({ price: t.stop, label: 'Initial stop', tone: 'down' });
    if (t.exit) l.push({ price: t.exit, label: 'Exit', tone: t.pnl >= 0 ? 'up' : 'down' });
    return l;
  }, [t]);
  const focus = useMemo(() => {
    if (!t) return undefined;
    const from = new Date(t.bar || t.entry_time || t.exit_time).getTime() / 1000;
    return { from, to: new Date(t.exit_time).getTime() / 1000 };
  }, [t]);
  if (!t) return null;
  const side = a?.sides[t.side];
  return (
    <>
      <div className="sheet-scrim" data-open={open} onClick={onClose} />
      <aside className="sheet" data-open={open} role="dialog" aria-modal="true" aria-label={`${coin(t.symbol)} ${t.side} trade`}
        onTransitionEnd={() => !open && setShown(null)}>
        <div className="sheet-head">
          <Coin symbol={t.symbol} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="t-title">{coin(t.symbol)} <SideTag side={t.side} /></div>
            <div className="t-small muted">{market(t.symbol)} · {t.timeframe} · {strategyName(t.strategy)} · {t.bot} bot</div>
          </div>
          <div className={`t-title-l num ${tone(t.pnl)}`} style={{ textAlign: 'right' }}>{usd(t.pnl, true)}<div className="t-small">{fmtR(t.r)}</div></div>
          <Btn kind="ghost" iconOnly icon="close" title="Close" onClick={onClose} />
        </div>
        <div className="sheet-body">
          <div className="facts num" style={{ margin: '0 -24px' }}>
            <div className="fact"><div className="k">Entry</div><div className="v">{price(t.entry)}</div><div className="t-small faint">{time(t.entry_time)}</div></div>
            <div className="fact"><div className="k">Exit</div><div className="v">{price(t.exit)}</div><div className="t-small faint">{time(t.exit_time)}</div></div>
            <div className="fact"><div className="k">Held</div><div className="v">{duration(t.entry_time, t.exit_time)}</div></div>
            <div className="fact"><div className="k">Risked</div><div className="v">{usd(t.risk_usd)}</div><div className="t-small faint">stop {price(t.stop)}</div></div>
            <div className="fact"><div className="k">Size</div><div className="v">{t.size}</div><div className="t-small faint">{t.leverage > 1 ? `${t.leverage}× · ` : ''}{usd(t.size * t.entry)}</div></div>
            <div className="fact"><div className="k">Entry slippage</div><div className="v">{t.slippage_bps === null ? '—' : `${t.slippage_bps > 0 ? '+' : ''}${t.slippage_bps} bps`}</div><div className="t-small faint">{t.entry_maker_share !== null ? `${Math.round((t.entry_maker_share || 0) * 100)}% limit fill` : ''}</div></div>
          </div>

          <section>
            <h4 className="t-title" style={{ marginBottom: 8 }}>The chart around it</h4>
            {err && <div className="banner bad"><Icon name="cloud_off" /><div className="grow">{err}</div></div>}
            {!a && !err && <Skeleton h={340} r={12} />}
            {a && <div className="panel" style={{ overflow: 'hidden' }}><PriceChart a={a} levels={levels} height={340} focus={focus} /></div>}
          </section>

          <section className="tonal side-col">
            <h4><Icon name="login" />Why it entered</h4>
            {t.bar ? <p className="muted t-small" style={{ marginBottom: 6 }}>The signal candle opened {time(t.bar)}. The order was filled {time(t.entry_time)}.</p> : null}
            {side ? <Checklist checks={side.checks} /> : a ? <p className="muted">No entry record for this trade in the log.</p> : <Skeleton h={60} />}
            <p className="muted t-small" style={{ marginTop: 6 }}>{a?.rule}</p>
          </section>

          <section className="tonal side-col">
            <h4><Icon name="logout" />How it ended</h4>
            <p><b style={{ fontWeight: 500 }}>{reasonLabel(t.reason)}.</b> {EXIT_STORY[t.reason] || ''}</p>
            <p className="muted t-small" style={{ marginTop: 6 }}>
              Result {usd(t.pnl, true)} after fees, {fmtR(t.r)} of the amount risked.
              {t.exit_maker_share !== null && ` ${Math.round((t.exit_maker_share || 0) * 100)}% of the exit filled as a limit order.`}
            </p>
          </section>
        </div>
      </aside>
    </>
  );
}

export function Trades({ data, route, go }: { data: ConsoleData; route: Extract<Route, { page: 'trades' }>; go: (r: Route) => void }) {
  const [bot, setBot] = useState<'all' | 'spot' | 'futures'>('all');
  const [result, setResult] = useState<'all' | 'won' | 'lost'>('all');
  const [q, setQ] = useState('');
  const [sort, setSort] = useState<{ k: SortKey; asc: boolean }>({ k: 'exit_time', asc: false });
  const all = data.trades;
  const rows = useMemo(() => {
    let r = (all || []).filter(t => (bot === 'all' || t.bot === bot) && (result === 'all' || (result === 'won' ? t.pnl > 0 : t.pnl <= 0))
      && (!q || t.symbol.toLowerCase().includes(q.toLowerCase()) || strategyName(t.strategy).toLowerCase().includes(q.toLowerCase())));
    r = [...r].sort((a, b) => {
      const va = a[sort.k] ?? 0, vb = b[sort.k] ?? 0;
      return (va < vb ? -1 : va > vb ? 1 : 0) * (sort.asc ? 1 : -1);
    });
    return r;
  }, [all, bot, result, q, sort]);
  const selected = (all || []).find(t => t.id === route.trade) || null;
  const total = rows.reduce((s, t) => s + t.pnl, 0);
  const th = (k: SortKey, label: string, right = false) => (
    <th className={right ? 'r' : ''} aria-sort={sort.k === k ? (sort.asc ? 'ascending' : 'descending') : 'none'}>
      <button data-active={sort.k === k} onClick={() => setSort(s => ({ k, asc: s.k === k ? !s.asc : false }))}>
        {label}<span className="icon">{sort.k === k && sort.asc ? 'arrow_upward' : 'arrow_downward'}</span>
      </button>
    </th>
  );

  return (
    <>
      <section className="panel">
        <div className="toolbar">
          <div className="filter-chips">
            {(['all', 'spot', 'futures'] as const).map(b => (
              <FilterChip key={b} on={bot === b} onClick={() => setBot(b)} count={b === 'all' ? all?.length : all?.filter(t => t.bot === b).length}>
                {b === 'all' ? 'All bots' : b === 'spot' ? 'Spot' : 'Futures'}
              </FilterChip>
            ))}
            <FilterChip on={result === 'won'} onClick={() => setResult(r => (r === 'won' ? 'all' : 'won'))}>Won</FilterChip>
            <FilterChip on={result === 'lost'} onClick={() => setResult(r => (r === 'lost' ? 'all' : 'lost'))}>Lost</FilterChip>
          </div>
          <span className="grow" />
          <label className="search"><Icon name="search" /><input value={q} onChange={e => setQ(e.target.value)} placeholder="Search coin or strategy" aria-label="Search trades" /></label>
        </div>
        {!all ? <div className="panel-body"><Skeleton h={240} /></div> : rows.length === 0 ? (
          <Empty icon="receipt_long" title={all.length ? 'No trades match these filters' : 'No closed trades yet'}>
            {all.length ? 'Clear a filter to see more.' : 'Closed trades appear here with the reason they were opened and closed.'}
          </Empty>
        ) : (
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  {th('symbol', 'Market')}<th>Side</th><th>Strategy</th><th className="r">Entry</th><th className="r">Exit</th><th>Ended by</th>
                  <th className="r hide-sm">Held</th>{th('r', 'R', true)}{th('pnl', 'P&L', true)}{th('exit_time', 'Closed', true)}
                </tr>
              </thead>
              <tbody>
                {rows.map(t => (
                  <tr key={t.id} className="clickable" aria-selected={t.id === route.trade} tabIndex={0}
                    onClick={() => go({ page: 'trades', trade: t.id })} onKeyDown={e => e.key === 'Enter' && go({ page: 'trades', trade: t.id })}>
                    <td><div className="sym"><Coin symbol={t.symbol} /><div><div className="name">{coin(t.symbol)}</div><div className="meta">{market(t.symbol)} · {t.timeframe}</div></div></div></td>
                    <td><SideTag side={t.side} /></td>
                    <td className="muted">{strategyName(t.strategy)}</td>
                    <td className="r num">{price(t.entry)}</td>
                    <td className="r num">{price(t.exit)}</td>
                    <td><Chip tone={t.pnl > 0 ? 'ok' : ''}>{reasonLabel(t.reason)}</Chip></td>
                    <td className="r num muted hide-sm">{duration(t.entry_time, t.exit_time)}</td>
                    <td className={`r num ${tone(t.r)}`}>{fmtR(t.r)}</td>
                    <td className={`r num ${tone(t.pnl)}`} style={{ fontWeight: 500 }}>{usd(t.pnl, true)}</td>
                    <td className="r num muted">{time(t.exit_time)}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr><td colSpan={8} className="muted">{rows.length} trade{rows.length === 1 ? '' : 's'}</td><td className={`r num ${tone(total)}`} style={{ fontWeight: 600 }}>{usd(total, true)}</td><td /></tr>
              </tfoot>
            </table>
          </div>
        )}
      </section>
      <TradeSheet trade={selected} onClose={() => go({ page: 'trades' })} />
    </>
  );
}
