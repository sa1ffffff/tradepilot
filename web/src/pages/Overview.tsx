import { useEffect, useRef, useState } from 'react';
import { BaselineSeries, ColorType, createChart, type UTCTimestamp } from 'lightweight-charts';
import type { ConsoleData, Route } from '../lib/store';
import { coin, reasonLabel, r as fmtR, strategyName, time, tone, until, usd } from '../lib/format';
import { BotHero } from '../components/Bots';
import { Positions } from '../components/Positions';
import { MoodTag, TriggerGauge } from '../components/Thinking';
import { Btn, Coin, Empty, Icon, Money, SideTag, Skeleton } from '../components/ui';

function EquityCurve({ points }: { points: [string, number][] }) {
  const el = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!el.current || points.length < 1) return;
    const s = getComputedStyle(document.documentElement);
    const v = (n: string) => s.getPropertyValue(n).trim();
    const chart = createChart(el.current, {
      autoSize: true,
      layout: { background: { type: ColorType.Solid, color: v('--surface') }, textColor: v('--ink-3'), fontFamily: v('--font'), fontSize: 11, attributionLogo: false },
      grid: { vertLines: { color: 'transparent' }, horzLines: { color: v('--line') } },
      rightPriceScale: { borderVisible: false },
      timeScale: {
        borderVisible: false, timeVisible: true,
        // a date where the day changes, the hour in between
        tickMarkFormatter: (t: number, kind: number) => new Date(t * 1000).toLocaleString([], kind < 3 ? { month: 'short', day: 'numeric' } : { hour: 'numeric' })
      },
      handleScroll: false, handleScale: false, crosshair: { vertLine: { labelVisible: false } }
    });
    const series = chart.addSeries(BaselineSeries, {
      baseValue: { type: 'price', price: 0 },
      topLineColor: v('--up'), topFillColor1: v('--up') + '33', topFillColor2: v('--up') + '05',
      bottomLineColor: v('--down'), bottomFillColor1: v('--down') + '05', bottomFillColor2: v('--down') + '33',
      lineWidth: 2, priceLineVisible: false, lastValueVisible: false
    });
    const seen = new Set<number>();
    const data = [{ t: new Date(points[0][0]).getTime() / 1000 - 3600, v: 0 }, ...points.map(([t, val]) => ({ t: new Date(t).getTime() / 1000, v: val }))]
      .map(p => { let t = Math.floor(p.t); while (seen.has(t)) t += 1; seen.add(t); return { time: t as UTCTimestamp, value: p.v }; });
    series.setData(data);
    chart.timeScale().fitContent();
    return () => chart.remove();
  }, [points]);
  return <div ref={el} style={{ height: 180 }} />;
}

export function Overview({ data, go, now }: { data: ConsoleData; go: (r: Route) => void; now: number }) {
  const { status: s, trades, overview } = data;
  // a dismissed health note stays hidden until the next check writes a new one
  const [hiddenNote, setHiddenNote] = useState(() => {
    try { return localStorage.getItem('tp-health-dismissed') || ''; } catch { return ''; }
  });
  const hideNote = (title: string) => {
    setHiddenNote(title);
    try { localStorage.setItem('tp-health-dismissed', title); } catch { /* private mode */ }
  };
  if (!s) {
    return (
      <div className="grid">
        <Skeleton h={112} r={16} />
        <div className="overview-grid"><Skeleton h={420} r={16} /><Skeleton h={420} r={16} /></div>
      </div>
    );
  }
  const p = s.pnl;
  const winRate = p.trades ? (p.wins / p.trades) * 100 : 0;
  const pf = p.gross_loss ? p.gross_win / Math.abs(p.gross_loss) : null;
  const tgt = s.target.daily_target_usd;
  const anyRunning = s.bots.spot.running || s.bots.futures.running;
  const rows = overview || [];
  const recent = (trades || []).slice(0, 6);

  return (
    <div className="grid" style={{ gap: 16 }}>
      {s.kill_switch && (
        <div className="banner warn"><Icon name="block" /><div className="grow"><b>New entries are paused.</b> Open positions are still managed and can exit.</div>
          <div className="actions"><Btn kind="text" small onClick={() => go({ page: 'controls' })}>Change</Btn></div></div>
      )}
      {s.target.reached && (
        <div className="banner ok"><Icon name="flag" fill /><div className="grow"><b>Daily target reached.</b> {usd(s.target.realized_today, true)} today; no new trades until 00:00 UTC.</div></div>
      )}
      {s.health.status === 'ATTENTION' && s.health.title !== hiddenNote && (
        <div className="banner bad"><Icon name="error" /><div className="grow"><b>Health check: needs attention.</b> {s.health.lines[0]}</div>
          <div className="actions"><Btn kind="text" small icon="close" iconOnly title="Dismiss until the next health check" aria-label="Dismiss" onClick={() => hideNote(s.health.title)} /></div></div>
      )}

      <BotHero status={s} overview={overview} refresh={data.refresh} now={now} go={go} />
      {!anyRunning && (
        <p className="hero-note muted t-small">
          <Icon name="info" /> Both bots are stopped, so nothing is being traded. The analysis below is still live: it shows what each strategy would do.
        </p>
      )}

      <section className="panel kpis" aria-label="Profit and loss">
        <div className="kpi">
          <div className="label"><Icon name="today" />Today, realized</div>
          <div className={`value ${tone(p.today_total)}`}><Money value={p.today_total} /></div>
          <div className="foot num">{tgt ? `${Math.max(0, Math.min(100, (p.today_total / tgt) * 100)).toFixed(0)}% of the ${usd(tgt)} target` : `Spot ${usd(p.today.spot, true)} · Futures ${usd(p.today.futures, true)}`}</div>
        </div>
        <div className="kpi">
          <div className="label"><Icon name="show_chart" />Open P&amp;L</div>
          <div className={`value ${tone(p.unrealized)}`}><Money value={p.unrealized} /></div>
          <div className="foot">{s.positions.length ? `${s.positions.length} open position${s.positions.length > 1 ? 's' : ''}` : 'No open positions'}</div>
        </div>
        <div className="kpi">
          <div className="label"><Icon name="account_balance" />Realized, all time</div>
          <div className={`value ${tone(p.all_time)}`}><Money value={p.all_time} /></div>
          <div className="foot num">{p.trades} closed trades on demo</div>
        </div>
        <div className="kpi">
          <div className="label"><Icon name="target" />Win rate</div>
          <div className="value num">{p.trades ? `${winRate.toFixed(0)}%` : '—'}</div>
          <div className="foot num">{p.wins} won · {p.trades - p.wins} lost{pf !== null ? ` · profit factor ${pf.toFixed(2)}` : ''}</div>
        </div>
      </section>

      <div className="overview-grid">
        <div className="grid" style={{ gap: 16 }}>
          <section className="panel" aria-labelledby="think-h">
            <div className="panel-head">
              <div>
                <h3 id="think-h">What the bots see now</h3>
                <div className="sub">Each strategy on its latest closed candle. Updates every minute.</div>
              </div>
              <Btn kind="text" small icon="arrow_forward" onClick={() => go({ page: 'strategies' })}>All</Btn>
            </div>
            <div className="think-list">
              {!overview && [0, 1, 2, 3].map(i => <div key={i} className="think" style={{ cursor: 'default' }}><Skeleton h={36} /><Skeleton h={36} /><Skeleton h={20} /></div>)}
              {rows.map(row => (
                <button key={row.bot + row.symbol} className="think" onClick={() => go({ page: 'strategies', bot: row.bot, symbol: row.symbol })}>
                  <div className="sym">
                    <Coin symbol={row.symbol} />
                    <div>
                      <div className="name">{coin(row.symbol)} <span className="faint t-small">{row.timeframe}</span></div>
                      <div className="meta">{strategyName(row.label)}{row.bot === 'spot' ? ' · spot' : ''}</div>
                    </div>
                  </div>
                  <div>
                    {row.error ? <div className="text down">Couldn't load candles: {row.error}</div> : (
                      <>
                        <div className="text">{row.headline}</div>
                        <div className="when"><MoodTag mood={row.mood} /> · next decision {until(row.next_decision, now)}</div>
                      </>
                    )}
                  </div>
                  {row.sides && row.close ? <TriggerGauge close={row.close} sides={row.sides} /> : <span />}
                </button>
              ))}
              {overview && rows.length === 0 && <Empty icon="tune" title="No strategies configured">Set STRATEGY_FILE and FUT_STRATEGY_FILE in .env.</Empty>}
            </div>
          </section>
          <Positions status={s} refresh={data.refresh} onOpen={pos => go({ page: 'strategies', bot: pos.bot, symbol: pos.symbol })} />
        </div>

        <div className="grid" style={{ gap: 16 }}>
          <section className="panel" aria-labelledby="curve-h">
            <div className="panel-head">
              <div><h3 id="curve-h">Realized P&amp;L</h3><div className="sub">Cumulative, after fees, both bots</div></div>
              <span className={`t-title num ${tone(p.all_time)}`}>{usd(p.all_time, true)}</span>
            </div>
            {p.curve.length ? <div style={{ padding: '0 8px 12px' }}><EquityCurve points={p.curve} /></div>
              : <Empty icon="monitoring" title="No closed trades yet" />}
          </section>
          <section className="panel" aria-labelledby="recent-h">
            <div className="panel-head">
              <div><h3 id="recent-h">Recent trades</h3></div>
              <Btn kind="text" small icon="arrow_forward" onClick={() => go({ page: 'trades' })}>History</Btn>
            </div>
            {recent.length === 0 ? <Empty icon="receipt_long" title="No trades yet" /> : (
              <div className="think-list">
                {recent.map(t => (
                  <button key={t.id} className="think" style={{ gridTemplateColumns: 'minmax(0,1fr) auto' }} onClick={() => go({ page: 'trades', trade: t.id })}>
                    <div className="sym"><Coin symbol={t.symbol} />
                      <div><div className="name">{coin(t.symbol)} <SideTag side={t.side} /></div><div className="meta">{reasonLabel(t.reason)} · {time(t.exit_time)}</div></div>
                    </div>
                    <div style={{ textAlign: 'right' }} className={`num ${tone(t.pnl)}`}>
                      <div style={{ fontWeight: 500 }}>{usd(t.pnl, true)}</div><div className="t-small">{fmtR(t.r)}</div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
