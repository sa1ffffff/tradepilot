import { useEffect, useMemo, useState } from 'react';
import { api, type Analysis, type BotName, type Slot } from '../lib/api';
import type { ConsoleData, Route } from '../lib/store';
import { ago, coin, market, price, strategyName, time, until } from '../lib/format';
import { PriceChart, type Level } from '../components/PriceChart';
import { Checklist, MoodTag, triggerLevel } from '../components/Thinking';
import { Btn, Chip, Coin, Empty, Icon, Skeleton } from '../components/ui';

export function useAnalysis(bot?: string, symbol?: string, trade?: string, every = 60_000) {
  const [a, setA] = useState<Analysis | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [tick, setTick] = useState(0);
  useEffect(() => {
    if (!bot || !symbol) return;
    let live = true;
    setErr(null);
    api.analysis(bot as BotName, symbol, trade).then(r => live && setA(r)).catch(e => live && setErr(String(e.message || e)));
    return () => { live = false; };
  }, [bot, symbol, trade, tick]);
  useEffect(() => {
    if (trade) return;
    const t = window.setInterval(() => document.visibilityState === 'visible' && setTick(x => x + 1), every);
    return () => clearInterval(t);
  }, [trade, every]);
  useEffect(() => setA(null), [bot, symbol, trade]);
  return { a, err, reload: () => setTick(x => x + 1) };
}

export function levelsFor(a: Analysis): Level[] {
  const out: Level[] = [];
  const pos = a.position as { entry?: number; stop?: number; tp?: number | null; dir?: number } | null | undefined;
  if (pos?.entry) {
    out.push({ price: pos.entry, label: 'Entry', tone: 'primary', dashed: false });
    if (pos.stop) out.push({ price: pos.stop, label: 'Stop', tone: 'down' });
    if (pos.tp) out.push({ price: pos.tp, label: 'Target', tone: 'up' });
    return out;
  }
  const lt = triggerLevel(a.sides.long);
  const st = triggerLevel(a.sides.short);
  if (lt) out.push({ price: lt, label: 'Long trigger', tone: 'up' });
  if (st) out.push({ price: st, label: 'Short trigger', tone: 'down' });
  return out;
}

function SideColumn({ name, side }: { name: 'long' | 'short'; side: NonNullable<Analysis['sides']['long']> }) {
  return (
    <div className="tonal side-col">
      <h4>
        <Icon name={name === 'long' ? 'north_east' : 'south_east'} className={name === 'long' ? 'up' : 'down'} />
        {name === 'long' ? 'Long entry' : 'Short entry'}
        <span className="grow" style={{ flex: 1 }} />
        <Chip tone={side.ready ? 'ok' : ''}>{side.ready ? 'Signal' : `${side.met} of ${side.total} met`}</Chip>
      </h4>
      <Checklist checks={side.checks} />
      <div className="trigger-line"><b>Waiting for</b> {side.trigger}.</div>
      <div className="trigger-line" style={{ marginTop: 6 }}><b>Exits on</b> {side.exit}.</div>
    </div>
  );
}

export function Evidence({ slot }: { slot: Slot }) {
  const e = slot.evidence;
  if (!e) return null;
  return (
    <section className="panel" aria-labelledby="ev-h">
      <div className="panel-head">
        <div><h3 id="ev-h">Research evidence</h3><div className="sub">Out-of-sample walk-forward, about 3 years, after costs, at {(slot.risk_fraction * 100).toFixed(0)}% risk per trade. Past results, not a forecast.</div></div>
        <Chip tone={e.verdict === 'CANDIDATE' ? 'ok' : 'warn'}>{e.verdict === 'CANDIDATE' ? 'Passed' : e.verdict}</Chip>
      </div>
      <div className="facts num">
        <div className="fact"><div className="k">Return</div><div className="v">{e.total_return_pct > 0 ? '+' : ''}{e.total_return_pct}%</div></div>
        <div className="fact"><div className="k">Profit factor</div><div className="v">{e.profit_factor}</div></div>
        <div className="fact"><div className="k">Win rate</div><div className="v">{e.win_rate_pct}%</div></div>
        <div className="fact"><div className="k">Trades</div><div className="v">{e.trades}</div></div>
        <div className="fact"><div className="k">Max drawdown</div><div className="v">{e.max_drawdown_pct}%</div></div>
        <div className="fact"><div className="k">Segments profitable</div><div className="v">{e.folds_positive} of 4</div></div>
      </div>
    </section>
  );
}

export function Strategies({ data, route, go, now }: { data: ConsoleData; route: Extract<Route, { page: 'strategies' }>; go: (r: Route) => void; now: number }) {
  const slots = data.status?.slots || [];
  const sel = useMemo(() => slots.find(s => s.bot === route.bot && s.symbol === route.symbol) || slots[0], [slots, route.bot, route.symbol]);
  const { a, err, reload } = useAnalysis(sel?.bot, sel?.symbol);
  const moods = Object.fromEntries((data.overview || []).map(o => [o.bot + o.symbol, o.mood]));
  useEffect(() => {
    // on phones the list is a horizontal strip; keep the selected one in view
    document.querySelector('.slot-btn[aria-current="true"]')?.scrollIntoView({ block: 'nearest', inline: 'center' });
  }, [sel]);

  if (!data.status) return <Skeleton h={500} r={16} />;
  if (!slots.length) return <Empty icon="tune" title="No strategies configured">Set STRATEGY_FILE and FUT_STRATEGY_FILE in .env, then reload.</Empty>;

  return (
    <div className="split">
      <nav className="panel slot-list" aria-label="Strategies">
        {slots.map(s => (
          <button key={s.bot + s.symbol} className="slot-btn" aria-current={s === sel}
            onClick={() => go({ page: 'strategies', bot: s.bot, symbol: s.symbol })}>
            <Coin symbol={s.symbol} />
            <span><span className="n">{coin(s.symbol)}</span> <span className="m">{s.timeframe}</span><div className="m trail">{strategyName(s.label)}{s.bot === 'spot' ? ' · spot' : ''}</div></span>
            <span className="trail">{moods[s.bot + s.symbol] === 'holding' ? <Icon name="trending_up" className="up" /> : moods[s.bot + s.symbol] === 'signal' ? <Icon name="bolt" fill /> : null}</span>
          </button>
        ))}
      </nav>

      {sel && (
        <div className="grid" style={{ gap: 16 }}>
          <section className="panel">
            <div className="panel-head" style={{ alignItems: 'flex-start' }}>
              <div className="sym">
                <Coin symbol={sel.symbol} size={40} />
                <div>
                  <h3 className="t-title-l" style={{ fontWeight: 450 }}>{coin(sel.symbol)} · {strategyName(sel.label)}</h3>
                  <div className="sub">{market(sel.symbol)} · {sel.timeframe} candles · {sel.bot} bot</div>
                </div>
              </div>
              <Btn kind="ghost" small icon="refresh" onClick={reload}>Refresh</Btn>
            </div>
            <div className="panel-body" style={{ paddingTop: 0 }}>
              <p className="muted" style={{ maxWidth: '80ch' }}>{sel.rule}</p>
            </div>
            {err && <div className="panel-body"><div className="banner bad"><Icon name="cloud_off" /><div className="grow">Couldn't load candles from OKX: {err}</div><div className="actions"><Btn kind="text" small onClick={reload}>Retry</Btn></div></div></div>}
            {!a && !err && <div className="panel-body"><Skeleton h={420} /></div>}
            {a && (
              <>
                <div className="panel-body" style={{ paddingTop: 0 }}>
                  <div className={`banner ${a.mood === 'signal' ? 'info' : a.mood === 'holding' ? 'ok' : ''}`}>
                    <Icon name="psychology" />
                    <div className="grow">
                      <div style={{ fontWeight: 500 }}>{a.headline}</div>
                      <div className="t-small" style={{ marginTop: 4, opacity: 0.85 }}>
                        <MoodTag mood={a.mood} /> · last candle closed {time(a.bar_close_time)} at {price(a.close)} · next decision {until(a.next_decision, now)} · updated {ago(data.updated ? new Date(data.updated).toISOString() : null, now)}
                      </div>
                    </div>
                  </div>
                </div>
                <PriceChart a={a} levels={levelsFor(a)} />
              </>
            )}
          </section>
          {a && (
            <div className="side-cols">
              {a.sides.long && <SideColumn name="long" side={a.sides.long} />}
              {a.sides.short ? <SideColumn name="short" side={a.sides.short} /> : (
                <div className="tonal side-col"><h4><Icon name="block" />Shorts</h4><p className="muted t-small">This strategy trades long only, so it never sells short.</p></div>
              )}
            </div>
          )}
          <Evidence slot={sel} />
        </div>
      )}
    </div>
  );
}
