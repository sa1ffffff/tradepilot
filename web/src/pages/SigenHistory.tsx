import { useCallback, useEffect, useMemo, useState } from 'react';
import { toast } from 'sonner';
import { sigenApi, type Analysis, type JournalReport, type JournalRow, type JournalSummary } from '../lib/api';
import type { Route } from '../lib/store';
import { ago, clock, duration, price, strategyName, time, tzName, validWindow } from '../lib/format';
import { PriceChart, type Level } from '../components/PriceChart';
import { Btn, Chip, Coin, Empty, FilterChip, Icon, SideTag, Skeleton } from '../components/ui';

const message = (e: unknown) => (e instanceof Error ? e.message : String(e));
const fmtR = (v: number | null | undefined) => (v === null || v === undefined ? '—' : `${v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v).toFixed(2)}R`);
const toneR = (v: number | null | undefined) => (!v ? '' : v > 0 ? 'up' : 'down');

const OUTCOME: Record<JournalRow['outcome']['status'], { tone: string; icon: string }> = {
  won: { tone: 'ok', icon: 'check_circle' },
  lost: { tone: 'bad', icon: 'cancel' },
  flat: { tone: '', icon: 'remove' },
  open: { tone: 'info', icon: 'pending' },
  'no data': { tone: '', icon: 'help' }
};

const ENDED: Record<string, string> = {
  tp: 'Take-profit hit', stop: 'Stop-loss hit', 'trailing stop': 'Trailing stop hit', signal: 'Exit rule fired'
};

function OutcomeChip({ o }: { o: JournalRow['outcome'] }) {
  const m = OUTCOME[o.status];
  return <Chip tone={m.tone} icon={m.icon}>{o.verdict}</Chip>;
}

/** The story of one signal, in words. */
function story(r: JournalRow): string {
  const o = r.outcome;
  const verb = r.market === 'spot' ? 'Buy' : r.direction === 'long' ? 'Long' : 'Short';
  const start = `${verb} ${r.coin} at ${price(r.entry)} after the ${clock(r.valid_from)} close`;
  if (o.status === 'open') return `${start}. Still open after ${o.bars_held} candle${o.bars_held === 1 ? '' : 's'}: ${fmtR(o.r_now)} so far, stop now ${price(o.stop_now)}.`;
  if (o.status === 'no data') return `${start}. ${o.note || "The candles needed to judge it aren't available yet."}`;
  const how = ENDED[o.exit_reason || ''] || 'Closed';
  const when = duration(r.valid_from, o.exit_time || null);
  return `${start}. ${how} ${when} later at ${price(o.exit_price)}, for ${fmtR(o.result_r)}.`;
}

function Kpis({ s, label }: { s: JournalSummary; label: string }) {
  const gap = s.win_rate_pct !== null && s.tested_win_rate_pct !== null ? s.win_rate_pct - s.tested_win_rate_pct : null;
  return (
    <div className="kpis">
      <div className="kpi"><div className="label"><Icon name="radar" />{label} signals</div><div className="value num">{s.signals}</div>
        <div className="foot">{s.closed} closed · {s.open} still open</div></div>
      <div className="kpi"><div className="label"><Icon name="task_alt" />Correct</div>
        <div className="value num">{s.win_rate_pct === null ? '—' : `${s.win_rate_pct.toFixed(0)}%`}</div>
        <div className="foot">{s.won} right, {s.lost} wrong, {s.flat} break-even</div></div>
      <div className="kpi"><div className="label"><Icon name="science" />Versus testing</div>
        <div className={`value num ${gap === null ? '' : gap >= 0 ? 'up' : 'down'}`}>{gap === null ? '—' : `${gap > 0 ? '+' : gap < 0 ? '−' : ''}${Math.abs(gap).toFixed(0)} pts`}</div>
        <div className="foot">{s.tested_win_rate_pct === null ? 'no closed signals yet' : `tested win rate was ${s.tested_win_rate_pct.toFixed(0)}%`}</div></div>
      <div className="kpi"><div className="label"><Icon name="functions" />Result</div>
        <div className={`value num ${toneR(s.total_r)}`}>{fmtR(s.total_r)}</div>
        <div className="foot">{s.avg_r === null ? 'R = the risk from entry to stop' : `${fmtR(s.avg_r)} per closed signal`}</div></div>
    </div>
  );
}

function ReportSheet({ r, onClose }: { r: JournalRow | null; onClose: () => void }) {
  const [open, setOpen] = useState(false);
  const [shown, setShown] = useState<JournalRow | null>(r);
  const [chart, setChart] = useState<Analysis | null>(null);
  const [chartErr, setChartErr] = useState<string | null>(null);
  useEffect(() => {
    if (r) { setShown(r); requestAnimationFrame(() => setOpen(true)); } else setOpen(false);
  }, [r]);
  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [onClose]);
  const id = shown?.id;
  useEffect(() => {
    if (!shown) return;
    let live = true;
    setChart(null); setChartErr(null);
    sigenApi.chart(shown.market, shown.coin).then(a => live && setChart(a)).catch(e => live && setChartErr(message(e)));
    return () => { live = false; };
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps
  const levels = useMemo<Level[]>(() => {
    if (!shown) return [];
    const l: Level[] = [{ price: shown.entry, label: 'Entry', tone: 'primary' }, { price: shown.stop, label: 'Stop-loss', tone: 'down' }];
    if (shown.target) l.push({ price: shown.target, label: 'Take profit', tone: 'up' });
    if (shown.outcome.exit_price) l.push({ price: shown.outcome.exit_price, label: 'Exit', tone: 'faint', dashed: true });
    return l;
  }, [shown]);
  if (!shown) return null;
  const t = shown;
  const o = t.outcome;
  const from = new Date(t.entry_bar).getTime() / 1000;
  const inChart = chart ? chart.candles.length > 0 && chart.candles[0][0] <= from : true;
  const focus = { from, to: o.exit_time ? new Date(o.exit_time).getTime() / 1000 : Date.now() / 1000 };
  const win = o.entry_window;
  return (
    <>
      <div className="sheet-scrim" data-open={open} onClick={onClose} />
      <aside className="sheet" data-open={open} role="dialog" aria-modal="true" aria-label={`${t.coin} signal report`}
        onTransitionEnd={() => !open && setShown(null)}>
        <div className="sheet-head">
          <Coin symbol={t.symbol} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="t-title">{t.coin} <SideTag side={t.direction} /> <span className="muted t-small">signal report</span></div>
            <div className="t-small muted">{t.market === 'spot' ? 'Spot' : 'Perpetual futures'} · {t.timeframe} · {strategyName(t.strategy)} · issued {time(t.valid_from)}</div>
          </div>
          <OutcomeChip o={o} />
          <Btn kind="ghost" iconOnly icon="close" title="Close" onClick={onClose} />
        </div>
        <div className="sheet-body">
          {t.source === 'replay' && <div className="banner info"><Icon name="replay" /><div className="grow"><b>Replay.</b> Re-created from candles with the strategy chosen in the latest scan, which was picked on data that includes this period. Shows how a signal plays out, not live accuracy.</div></div>}
          {t.late && <div className="banner warn"><Icon name="schedule" /><div className="grow">Logged after its entry candle (the console wasn't running when it fired). The plan is the same; the issue time is the entry candle's close.</div></div>}

          <section className={`sg-verdict ${o.status}`}>
            <div className="sg-verdict-top">
              <Icon name={OUTCOME[o.status].icon} />
              <div>
                <div className="v">{o.verdict}</div>
                <div className="t-small muted">{o.status === 'open' ? 'judged when it closes' : o.status === 'no data' ? '' : `the signal's own plan, before fees · ±${0.05}R counts as break-even`}</div>
              </div>
              <div className={`r num ${toneR(o.result_r ?? o.r_now)}`}>{fmtR(o.result_r ?? o.r_now)}</div>
            </div>
            <p>{story(t)}</p>
          </section>

          <div className="facts three num panel" style={{ overflow: 'hidden' }}>
            <div className="fact"><div className="k">Valid for entry</div><div className="v">{validWindow(t.valid_from, t.valid_until)}</div><div className="t-small faint">your time ({Intl.DateTimeFormat().resolvedOptions().timeZone})</div></div>
            <div className="fact"><div className="k">Entry</div><div className="v">{price(t.entry)}</div><div className="t-small faint">{t.chase_limit ? `don't chase past ${price(t.chase_limit)}` : ''}</div></div>
            <div className="fact"><div className="k">Could you get in?</div><div className={`v ${win ? (win.enterable ? 'up' : 'down') : ''}`}>{win ? (win.enterable ? 'Yes' : 'No') : '—'}</div>
              <div className="t-small faint">{win ? `next candle opened at ${price(win.next_open)}` : 'next candle not closed yet'}</div></div>
            <div className="fact"><div className="k">Stop-loss</div><div className="v down">{price(t.stop)}</div><div className="t-small faint">{o.trail_moved ? 'trailed later' : 'did not move'}</div></div>
            <div className="fact"><div className="k">Take profit</div><div className="v up">{t.target ? price(t.target) : 'Exit rule'}</div><div className="t-small faint">{t.target ? '' : t.exit_rule || ''}</div></div>
            <div className="fact"><div className="k">{o.status === 'open' ? 'Price now' : 'Exit'}</div><div className="v">{price(o.exit_price ?? o.price)}</div>
              <div className="t-small faint">{o.exit_time ? `${ENDED[o.exit_reason || ''] || ''}, ${time(o.exit_time)}` : o.as_of ? `as of ${time(o.as_of)}` : ''}</div></div>
            <div className="fact"><div className="k">Best it got</div><div className="v up">{fmtR(o.mfe_r)}</div><div className="t-small faint">max favourable move</div></div>
            <div className="fact"><div className="k">Worst it got</div><div className="v down">{fmtR(o.mae_r)}</div><div className="t-small faint">max adverse move</div></div>
            <div className="fact"><div className="k">Held</div><div className="v">{o.bars_held !== undefined ? `${o.bars_held} candle${o.bars_held === 1 ? '' : 's'}` : '—'}</div><div className="t-small faint">{o.bars_held !== undefined ? `${o.bars_held * 4} hours` : ''}</div></div>
          </div>

          <section>
            <h4 className="t-title" style={{ marginBottom: 8 }}>The chart</h4>
            {chartErr && <div className="banner bad"><Icon name="cloud_off" /><div className="grow">{chartErr}</div></div>}
            {!chart && !chartErr && <Skeleton h={320} r={12} />}
            {chart && <div className="panel" style={{ overflow: 'hidden' }}><PriceChart a={chart} levels={levels} height={320} focus={inChart ? focus : undefined} /></div>}
            {chart && !inChart && <p className="t-small faint" style={{ marginTop: 6 }}>The entry is older than the chart's 160 candles; the levels are drawn on today's chart.</p>}
          </section>

          <section className="tonal side-col">
            <h4><Icon name="description" />As issued</h4>
            <p>{t.instruction}</p>
            <p className="muted t-small" style={{ marginTop: 6 }}>Confidence {t.confidence.score}/100 ({t.confidence.label}). Tested win rate {t.tested.win_rate_pct.toFixed(0)}% over {t.tested.trades} trades. Logged {time(t.recorded_at)}. {t.rule}</p>
          </section>

          <p className="sg-disclaimer"><Icon name="info" />Results use the signal's own entry, stop, target and exit rule, before fees and slippage. Real fills differ. Not financial advice.</p>
        </div>
      </aside>
    </>
  );
}

type Source = 'live' | 'replay';
type Result = 'all' | 'won' | 'lost' | 'open';

export function SigenHistory({ route, go, now }: { route: Extract<Route, { page: 'sigen' }>; go: (r: Route) => void; now: number }) {
  const [rep, setRep] = useState<JournalReport | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [source, setSource] = useState<Source | null>(null);
  const [market, setMarket] = useState<'all' | 'spot' | 'futures'>('all');
  const [result, setResult] = useState<Result>('all');

  const load = useCallback(async () => {
    try { setRep(await sigenApi.journal()); setErr(null); } catch (e) { setErr(message(e)); }
  }, []);
  useEffect(() => {
    load();
    const t = window.setInterval(() => document.visibilityState === 'visible' && load(), 300_000);
    return () => clearInterval(t);
  }, [load]);

  const rows = rep?.signals || [];
  const src: Source = source || (rep && rep.summary.live.signals === 0 ? 'replay' : 'live');
  const shown = rows.filter(r => r.source === src && (market === 'all' || r.market === market)
    && (result === 'all' || (result === 'open' ? r.outcome.status === 'open' : r.outcome.status === result)));
  const selected = rows.find(r => r.id === route.item) || null;

  const replay = async () => {
    setBusy(true);
    const r = await sigenApi.backfill(30);
    setBusy(false);
    if (r.ok) toast.success(r.message); else toast.error(r.message);
    load();
  };

  if (!rep) {
    return err
      ? <div className="banner bad"><Icon name="cloud_off" /><div className="grow">Can't load the signal history: {err}</div><div className="actions"><Btn kind="text" small onClick={load}>Retry</Btn></div></div>
      : <Skeleton h={420} r={16} />;
  }
  const live = rep.summary.live;
  const first = rows.filter(r => r.source === 'live').map(r => r.recorded_at).sort()[0];

  return (
    <>
      {live.signals === 0 && (
        <div className="banner info">
          <Icon name="info" />
          <div className="grow">
            <b>No live signals logged yet.</b> The console logs every new signal at each 4h close while it runs; each one is judged once its stop, target or exit rule ends it.
            {rep.summary.replay.signals > 0 ? ' Meanwhile, the replay below shows how the last 30 days of signals would have turned out.' : ' Replay the last 30 days to see how signals resolve.'}
          </div>
          {rep.summary.replay.signals === 0 && <div className="actions"><Btn kind="tonal" small icon="replay" busy={busy} onClick={replay}>Replay 30 days</Btn></div>}
        </div>
      )}

      <section className="panel">
        <div className="panel-head">
          <div><h3>{src === 'live' ? 'Live signals' : 'Replay, last 30 days'}</h3>
            <div className="sub">{src === 'live' ? `Logged as issued${first ? ` since ${time(first)}` : ''}; nothing is edited afterwards` : "Today's strategies run over recent candles; picked with hindsight, so read it as a demonstration"}</div></div>
          <span className="t-small faint">Updated {ago(rep.generated_at, now)}</span>
        </div>
        <Kpis s={rep.summary[src]} label={src === 'live' ? 'Live' : 'Replayed'} />
      </section>

      <section className="panel">
        <div className="toolbar">
          <div className="filter-chips">
            {(['live', 'replay'] as const).map(k => <FilterChip key={k} on={src === k} onClick={() => setSource(k)} count={rep.summary[k].signals}>{k === 'live' ? 'Live' : 'Replay'}</FilterChip>)}
            <span className="sg-chip-gap" />
            {(['all', 'spot', 'futures'] as const).map(k => <FilterChip key={k} on={market === k} onClick={() => setMarket(k)}>{k === 'all' ? 'Both markets' : k === 'spot' ? 'Spot' : 'Futures'}</FilterChip>)}
            <span className="sg-chip-gap" />
            {(['won', 'lost', 'open'] as const).map(k => <FilterChip key={k} on={result === k} onClick={() => setResult(x => (x === k ? 'all' : k))}>{k === 'won' ? 'Correct' : k === 'lost' ? 'Wrong' : 'Still open'}</FilterChip>)}
          </div>
          <span className="grow" />
          {rep.summary.replay.signals > 0 && src === 'replay' && <Btn kind="text" small icon="replay" busy={busy} onClick={replay}>Update replay</Btn>}
          <a className="btn outlined sm" href={sigenApi.journalCsv} download><span className="icon">download</span>Download report</a>
        </div>
        {shown.length === 0 ? (
          <Empty icon="history" title={rows.length ? 'No signals match these filters' : 'No signals logged yet'}>
            {rows.length ? 'Clear a filter to see more.' : 'Signals appear here as SiGen issues them, with a verdict once each one ends.'}
          </Empty>
        ) : (
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr><th>Issued ({tzName()})</th><th>Coin</th><th>Signal</th><th className="r">Entry</th><th className="r hide-sm">Stop-loss</th><th>Verdict</th><th className="r">Result</th><th className="hide-sm">How it ended</th></tr>
              </thead>
              <tbody>
                {shown.map(r => (
                  <tr key={r.id} className="clickable" tabIndex={0} aria-selected={r.id === route.item}
                    onClick={() => go({ page: 'sigen', view: 'history', item: r.id })}
                    onKeyDown={e => e.key === 'Enter' && go({ page: 'sigen', view: 'history', item: r.id })}>
                    <td className="num">{clock(r.valid_from)}{r.late && <span className="faint t-small"> · late</span>}</td>
                    <td><div className="sym"><Coin symbol={r.symbol} /><div><div className="name">{r.coin}</div><div className="meta">{r.market === 'spot' ? 'Spot' : 'Futures'} · {strategyName(r.strategy)}</div></div></div></td>
                    <td><SideTag side={r.direction} /></td>
                    <td className="r num">{price(r.entry)}</td>
                    <td className="r num hide-sm down">{price(r.stop)}</td>
                    <td><OutcomeChip o={r.outcome} /></td>
                    <td className={`r num ${toneR(r.outcome.result_r ?? r.outcome.r_now)}`} style={{ fontWeight: 500 }}>{fmtR(r.outcome.result_r ?? r.outcome.r_now)}{r.outcome.status === 'open' && <span className="faint t-small"> so far</span>}</td>
                    <td className="muted hide-sm">{r.outcome.status === 'open' ? `${r.outcome.bars_held} candles in` : ENDED[r.outcome.exit_reason || ''] || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <p className="sg-disclaimer"><Icon name="info" />A signal is correct if its own plan (entry, stop-loss, target, exit rule) ended above +0.05R, before fees. Past signals don't predict future ones.</p>
      <ReportSheet r={selected} onClose={() => go({ page: 'sigen', view: 'history' })} />
    </>
  );
}
