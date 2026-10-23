import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { toast } from 'sonner';
import { sigenApi, type Analysis, type Signal, type SigenMarket, type SigenSignals, type SigenStatus, type SigenTerms } from '../lib/api';
import type { Route } from '../lib/store';
import { ago, clock, price, strategyName, time, tzName, until } from '../lib/format';
import { SigenHistory } from './SigenHistory';
import { PriceChart, type Level } from '../components/PriceChart';
import { Checklist } from '../components/Thinking';
import { Btn, Chip, Coin, Dialog, Empty, Icon, Segmented, Skeleton } from '../components/ui';
import '../sigen.css';

const visible = () => document.visibilityState === 'visible';
const message = (e: unknown) => (e instanceof Error ? e.message : String(e));
/** "3 years" / "11 months" of history the strategy was tested on. */
const span = (days?: number) => (!days ? '3 years' : days >= 700 ? `${Math.round(days / 365)} years` : days >= 330 ? '1 year' : `${Math.round(days / 30)} months`);
const pctFrom = (level: number, from: number) => {
  const v = (level / from - 1) * 100;
  return `${v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v).toFixed(2)}%`;
};

function useSigen(market: SigenMarket) {
  const [status, setStatus] = useState<SigenStatus | null>(null);
  const [signals, setSignals] = useState<Partial<Record<SigenMarket, SigenSignals>>>({});
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadStatus = useCallback(async () => {
    try { setStatus(await sigenApi.status()); setErr(null); } catch (e) { setErr(message(e)); }
  }, []);
  const loadSignals = useCallback(async (m: SigenMarket) => {
    setLoading(true);
    try {
      const d = await sigenApi.signals(m);
      setSignals(x => ({ ...x, [m]: d }));
      setErr(null);
    } catch (e) { setErr(message(e)); }
    setLoading(false);
  }, []);

  useEffect(() => { loadStatus(); }, [loadStatus]);
  const accepted = !!status?.terms.accepted;
  const running = status?.scan.state === 'running';
  const generated = status?.generated_at;
  useEffect(() => {
    if (!accepted || !generated) return;
    loadSignals(market);
    const t = window.setInterval(() => visible() && loadSignals(market), 60_000);
    return () => clearInterval(t);
  }, [accepted, generated, market, loadSignals]);
  useEffect(() => {
    const t = window.setInterval(() => visible() && loadStatus(), running ? 3000 : 60_000);
    return () => clearInterval(t);
  }, [running, loadStatus]);

  return { status, data: signals[market], err, loading, loadStatus, loadSignals };
}

/* ---------- terms gate ---------- */

function TermsText({ terms }: { terms: SigenTerms }) {
  return (
    <div className="sg-terms-text">
      {terms.sections.map(([h, p]) => (
        <section key={h}><h4>{h}</h4><p>{p}</p></section>
      ))}
    </div>
  );
}

function TermsGate({ terms, onAccepted }: { terms: SigenTerms; onAccepted: () => void }) {
  const [ticked, setTicked] = useState<Set<string>>(new Set());
  const [name, setName] = useState('');
  const [busy, setBusy] = useState(false);
  const [read, setRead] = useState(false);
  const ready = ticked.size === terms.statements.length && name.trim().length >= 2;
  const toggle = (k: string) => setTicked(s => { const n = new Set(s); if (n.has(k)) n.delete(k); else n.add(k); return n; });
  const submit = async () => {
    setBusy(true);
    const r = await sigenApi.accept(name, [...ticked], terms.version);
    setBusy(false);
    if (r.ok) { toast.success(r.message); onAccepted(); } else toast.error(r.message);
  };
  return (
    <section className="panel sg-gate fade-in">
      <div className="sg-gate-head">
        <span className="sg-gate-icon"><Icon name="gavel" /></span>
        <div>
          <h3>Before you use SiGen</h3>
          <p className="muted">SiGen's signals come from AI and automated rules, and they can be wrong. Read the terms and accept them once to continue.</p>
        </div>
      </div>
      <div className="sg-terms-box" tabIndex={0} aria-label={terms.title}
        onScroll={e => { const el = e.currentTarget; if (el.scrollTop + el.clientHeight >= el.scrollHeight - 24) setRead(true); }}>
        <h4 className="t-title">{terms.title}</h4>
        <p className="t-small faint" style={{ marginBottom: 4 }}>Version {terms.version}</p>
        <TermsText terms={terms} />
      </div>
      {!read && <p className="t-small faint sg-scroll-hint"><Icon name="south" />Scroll to the end of the terms to continue.</p>}
      <fieldset className="sg-statements" disabled={!read}>
        <legend className="t-title-s">I declare that</legend>
        {terms.statements.map(([k, text]) => (
          <label key={k} className="sg-check">
            <input type="checkbox" checked={ticked.has(k)} onChange={() => toggle(k)} />
            <span>{text}</span>
          </label>
        ))}
        <div className="field" style={{ marginTop: 8 }}>
          <label htmlFor="sg-name">Your full name, as your signature</label>
          <div className="box"><input id="sg-name" value={name} onChange={e => setName(e.target.value)} autoComplete="name" placeholder="e.g. Alex Morgan" maxLength={120} /></div>
          <div className="help">Signed {new Date().toLocaleDateString([], { year: 'numeric', month: 'long', day: 'numeric' })}. Stored on this computer with the terms version.</div>
        </div>
      </fieldset>
      <div className="sg-gate-actions">
        <span className="t-small faint">{!read ? 'Read the terms first' : !ready ? 'Tick every statement and sign with your name' : 'You can read the terms again any time from this page.'}</span>
        <Btn icon="verified_user" disabled={!ready || !read} busy={busy} onClick={submit}>Accept and continue</Btn>
      </div>
    </section>
  );
}

/* ---------- signal pieces ---------- */

const STATE: Record<Signal['state'], { label: string; icon: string; tone: string }> = {
  entry: { label: 'Enter now', icon: 'bolt', tone: 'info' },
  exit: { label: 'Close now', icon: 'logout', tone: 'warn' },
  holding: { label: 'Open trade', icon: 'trending_up', tone: 'ok' },
  armed: { label: 'Not yet', icon: 'hourglass_top', tone: '' },
  held: { label: 'Skipped', icon: 'pause_circle', tone: 'warn' },
  watching: { label: 'No setup', icon: 'visibility', tone: '' }
};

function StateChip({ s }: { s: Signal }) {
  const m = STATE[s.state];
  return <Chip tone={m.tone} icon={m.icon}>{m.label}</Chip>;
}

type Side = 'long' | 'short' | 'buy' | 'none';
const sideOf = (s: Signal): Side => (s.state === 'watching' || !s.direction ? 'none' : s.market === 'spot' ? 'buy' : s.direction);
const SIDE: Record<Side, { word: string; icon: string; hint: string }> = {
  long: { word: 'LONG', icon: 'north_east', hint: 'You make money if the price goes up' },
  short: { word: 'SHORT', icon: 'south_east', hint: 'You make money if the price goes down' },
  buy: { word: 'BUY', icon: 'north_east', hint: 'You make money if the price goes up' },
  none: { word: 'NO TRADE', icon: 'remove', hint: 'Nothing to do on this coin yet' }
};

/** The one thing every signal must make obvious: which way the trade goes. */
export function DirBadge({ s, big }: { s: Signal; big?: boolean }) {
  const k = sideOf(s);
  return <span className={`sg-dir ${k}${big ? ' big' : ''}`}><Icon name={SIDE[k].icon} />{SIDE[k].word}</span>;
}

/** "+2.0× risk": results measured in what the trade put at risk (entry to stop-loss). */
export const timesRisk = (v: number | null | undefined) =>
  v === null || v === undefined ? '—' : `${v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v).toFixed(1)}× risk`;

const EXIT_REASON: Record<string, string> = {
  stop: 'The price reached the stop-loss', tp: 'The price reached the take-profit',
  signal: "The strategy's exit condition was met", liquidated: 'The position was liquidated'
};

type Row = { k: string; v: ReactNode; d?: ReactNode; tone?: string };

/** The trade plan: the same rows, in the same order, for every signal. */
function Plan({ s }: { s: Signal }) {
  const k = sideOf(s);
  const up = k !== 'short';
  const word = SIDE[k].word;
  const tz = tzName(new Date(s.valid_until));
  const rows: Row[] = [];
  const base = s.state === 'holding' ? s.price : s.entry ?? s.price;
  const from = s.state === 'holding' ? 'from the current price' : 'from entry';
  const stopRow = (label = 'Stop-loss'): Row => ({
    k: label, v: price(s.stop), tone: 'down',
    d: <>{pctFrom(s.stop as number, base)} {from}. Close the trade if the price {up ? 'falls' : 'rises'} to this.</>
  });
  const targetRow = (): Row => (s.target !== null
    ? { k: 'Take-profit', v: price(s.target), tone: 'up', d: <>{pctFrom(s.target, base)} {from}. Close the trade here to take the profit.</> }
    : { k: 'Take-profit', v: 'None', d: s.trail ? 'Keep the trade until SiGen says close. Once you are well in profit, SiGen raises the stop-loss to protect it.' : 'Keep the trade until SiGen says close.' });

  if (s.state === 'entry') {
    rows.push({ k: 'What to do', v: s.market === 'spot' ? 'Buy now' : `Open a ${word} now` });
    rows.push({ k: 'Entry price', v: <>about {price(s.entry)}</>, d: 'The latest 4-hour closing price.' });
    rows.push(stopRow(), targetRow());
    if (s.chase_limit != null) rows.push({ k: "Don't enter if", v: <>the price is {up ? 'above' : 'below'} {price(s.chase_limit)}</>, d: 'Past this, the trade is no longer the one that was tested.' });
    rows.push({ k: 'Valid until', v: `${clock(s.valid_until)} ${tz}`, d: 'Your time. After this, ignore the entry.' });
  } else if (s.state === 'armed' || s.state === 'held') {
    const above = (s.entry ?? 0) > s.price;
    rows.push(s.state === 'held'
      ? { k: 'What to do', v: 'Skip this one', tone: 'warn', d: 'The market is too choppy for this kind of signal.' }
      : { k: 'What to do', v: 'Wait', d: <>Enter only if a 4-hour candle closes {above ? 'above' : 'below'} {price(s.entry)}.</> });
    rows.push({ k: s.state === 'held' ? 'Entry would be' : 'Entry price', v: price(s.entry), d: `${pctFrom(s.entry as number, s.price)} from the current price.` });
    if (s.stop !== null) rows.push(stopRow());
    rows.push(targetRow());
    rows.push({ k: 'Next check', v: `${clock(s.valid_until)} ${tz}`, d: 'Your time, when the current 4-hour candle closes.' });
  } else if (s.state === 'holding') {
    rows.push({ k: 'What to do', v: s.market === 'spot' ? 'Keep holding' : `Keep the ${word} open` });
    rows.push({ k: 'Entered at', v: price(s.entry), d: time(s.signal_time) });
    rows.push(stopRow('Stop-loss now'), targetRow());
    rows.push(s.late_entry_ok
      ? { k: 'Joining late?', v: <>Only while the price is {up ? 'below' : 'above'} {price(s.chase_limit)}</>, d: <>If it is already {up ? 'above' : 'below'} that, you have missed this one. Use the same stop-loss.</> }
      : { k: 'Joining late?', v: 'Too late for this one', tone: 'warn', d: 'The price has moved too far since the entry.' });
    rows.push({ k: 'So far', v: timesRisk(s.r_now), tone: (s.r_now ?? 0) >= 0 ? 'up' : 'down', d: `Price ${pctFrom(s.price, s.entry as number)} since the entry.` });
  } else if (s.state === 'exit') {
    rows.push({ k: 'What to do', v: s.market === 'spot' ? 'Sell now' : `Close the ${word} now` });
    rows.push({ k: 'Why', v: EXIT_REASON[s.exit_reason || 'signal'] || EXIT_REASON.signal });
    rows.push({ k: 'Entered at', v: price(s.entry), d: time(s.signal_time) });
    rows.push({ k: 'Closing price', v: price(s.exit_price), d: 'The latest 4-hour close.' });
    rows.push({ k: 'Result', v: timesRisk(s.result_r), tone: (s.result_r ?? 0) >= 0 ? 'up' : 'down', d: s.exit_price && s.entry ? `${pctFrom(s.exit_price, s.entry)} price move.` : undefined });
    rows.push({ k: 'Close by', v: `${clock(s.valid_until)} ${tz}`, d: 'Your time.' });
  } else {
    rows.push({ k: 'What to do', v: 'Nothing yet', d: 'There is no setup on this coin right now.' });
    rows.push({ k: 'Next check', v: `${clock(s.valid_until)} ${tz}`, d: 'Your time, when the current 4-hour candle closes.' });
  }
  return (
    <dl className="sg-plan num">
      {rows.map(r => (
        <div key={r.k} className={r.tone || ''}>
          <dt>{r.k}</dt>
          <dd><span className="v">{r.v}</span>{r.d && <span className="d">{r.d}</span>}</dd>
        </div>
      ))}
    </dl>
  );
}

function ConfidenceMeter({ c, big }: { c: Signal['confidence']; big?: boolean }) {
  return (
    <div className={`sg-conf ${c.label.toLowerCase()}${big ? ' big' : ''}`}>
      <div className="k">Confidence</div>
      <div className="v num">{c.score}<span className="of">/100</span><span className="lbl">{c.label}</span></div>
      <div className="meter" role="img" aria-label={`Confidence ${c.score} out of 100, ${c.label}`}><span style={{ width: `${c.score}%` }} /></div>
    </div>
  );
}

function PastRecord({ a }: { a: Signal['accuracy'] }) {
  const ratio = a.avg_loss_r > 0 ? a.avg_win_r / a.avg_loss_r : null;
  return (
    <div className="sg-acc">
      <div className="k">Past record</div>
      <div className="v num">{a.win_rate_pct.toFixed(0)}%<span className="of">won</span></div>
      <div className="t-small muted num">of {a.trades} past trades{a.history_days && a.history_days < 700 ? ` (only ${span(a.history_days)} of data)` : ''}{ratio ? ` · wins were ${ratio.toFixed(1)}× the size of losses` : ''}</div>
    </div>
  );
}

const MEASURE: Record<string, string> = {
  er_30: 'trend clarity over the last 30 candles', er_60: 'trend clarity over the last 60 candles', chop_14: 'the choppiness index',
  adx_14: 'trend strength (ADX)', btc_er_30: "Bitcoin's trend clarity", btc_chop_14: "Bitcoin's choppiness index"
};
const ruleText = (r: { measure: string; side: string; threshold: number }) => `${MEASURE[r.measure] || r.measure} is ${r.side === 'below' ? 'below' : 'above'} ${r.threshold}`;

/** One line on the card when the market is choppy and the filter (on or on trial) would skip it. */
function RegimeNote({ s }: { s: Signal }) {
  const g = s.regime;
  if (!g || !g.would_hold || s.state === 'held') return null;
  return (
    <div className="sg-regime-note"><Icon name="waves" /><span><b>Choppy market.</b> Prices here have been moving sideways. A filter being tried out would skip this signal; it isn't switched on, so the signal stands.</span></div>
  );
}

function RegimeSection({ s }: { s: Signal }) {
  const g = s.regime;
  if (!g) return null;
  const er = g.er_30;
  const read = er === null ? 'not enough data' : er < 0.2 ? 'choppy: back and forth' : er < 0.35 ? 'mixed' : 'clear trend';
  return (
    <section className="tonal side-col">
      <h4><Icon name="waves" />Trending or choppy?</h4>
      <div className="sg-regime num">
        <div><span className="k">Trend clarity</span><span className="v">{er ?? '—'}</span><span className="d">{read} (0 = sideways, 1 = straight line)</span></div>
        <div><span className="k">Choppiness</span><span className="v">{g.chop_14 ?? '—'}</span><span className="d">above 62 means sideways</span></div>
        <div><span className="k">Trend strength</span><span className="v">{g.adx_14 ?? '—'}</span><span className="d">below 20 means weak</span></div>
      </div>
      <p className="muted t-small" style={{ marginTop: 8 }}>
        {!g.trend_strategy ? 'This strategy bets on prices bouncing back, which works best in choppy markets, so the choppy-market filter never applies to it.'
          : g.mode === 'on' ? (g.held_back ? `Skipped, because ${ruleText(g.rule!)}.` : `The choppy-market filter is on, and this market passes it.`)
          : g.mode === 'shadow' ? `The choppy-market filter is not switched on: it made results worse in testing (see How SiGen works). A version is being tried out on live signals, and it ${g.would_hold ? 'would skip' : 'would keep'} this one. The Signal history page tracks whether skipping would have helped.`
          : 'No choppy-market filter is set.'}
      </p>
    </section>
  );
}

function SignalTicket({ s, onOpen, now }: { s: Signal; onOpen: () => void; now: number }) {
  const k = sideOf(s);
  const tone = s.state === 'exit' ? 'exit' : k === 'short' ? 'short' : k === 'none' ? 'none' : 'long';
  return (
    <button type="button" className={`sg-ticket ${tone} ${s.state}`} onClick={onOpen}>
      <div className="sg-ticket-top">
        <Coin symbol={s.symbol} size={40} />
        <div className="who">
          <div className="t-title">{s.coin}</div>
          <div className="t-small muted">{s.market === 'spot' ? 'Spot' : 'Futures'} · {strategyName(s.strategy)}</div>
        </div>
        <StateChip s={s} />
      </div>
      <div className="sg-side"><DirBadge s={s} big /><span className="hint">{SIDE[k].hint}</span></div>
      <Plan s={s} />
      <RegimeNote s={s} />
      <div className="sg-scores">
        <ConfidenceMeter c={s.confidence} />
        <PastRecord a={s.accuracy} />
      </div>
      <div className="sg-ticket-foot t-small muted">
        <span><Icon name="update" />Next check {until(s.next_decision, now)}</span>
        <span className="open">Details<Icon name="chevron_right" /></span>
      </div>
    </button>
  );
}

function ArmedTable({ rows, onOpen, selected }: { rows: Signal[]; onOpen: (s: Signal) => void; selected?: string }) {
  return (
    <div className="table-wrap">
      <table className="data sg-table">
        <thead>
          <tr><th>Coin</th><th>Trade</th><th className="r">Enter only if a 4-hour candle closes</th><th className="r hide-sm">Stop-loss</th><th className="r hide-sm">Take-profit</th><th className="r">Confidence</th><th className="r hide-sm">Past record</th></tr>
        </thead>
        <tbody>
          {rows.map(s => (
            <tr key={s.id} className="clickable" tabIndex={0} aria-selected={s.coin === selected}
              onClick={() => onOpen(s)} onKeyDown={e => e.key === 'Enter' && onOpen(s)}>
              <td><div className="sym"><Coin symbol={s.symbol} /><div><div className="name">{s.coin}</div><div className="meta">{strategyName(s.strategy)}</div></div></div></td>
              <td><DirBadge s={s} /></td>
              <td className="r num">{s.entry !== null && s.entry < s.price ? 'below' : 'above'} {price(s.entry)}<div className="t-small faint">{s.entry !== null ? `${pctFrom(s.entry, s.price)} from now` : ''}</div></td>
              <td className="r num hide-sm"><span className="down">{price(s.stop)}</span><div className="t-small faint">{s.stop !== null && s.entry !== null ? pctFrom(s.stop, s.entry) : ''}</div></td>
              <td className="r num hide-sm">{s.target !== null && s.entry !== null ? <><span className="up">{price(s.target)}</span><div className="t-small faint">{pctFrom(s.target, s.entry)}</div></> : <span className="faint">none: SiGen says when</span>}</td>
              <td className="r num"><span className={`sg-score ${s.confidence.label.toLowerCase()}`}>{s.confidence.score}</span></td>
              <td className="r num hide-sm">won {s.accuracy.win_rate_pct.toFixed(0)}% <span className="faint">of {s.accuracy.trades}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ---------- detail sheet ---------- */

function SignalSheet({ s, onClose, now }: { s: Signal | null; onClose: () => void; now: number }) {
  const [open, setOpen] = useState(false);
  const [shown, setShown] = useState<Signal | null>(s);
  const [chart, setChart] = useState<Analysis | null>(null);
  const [chartErr, setChartErr] = useState<string | null>(null);
  useEffect(() => {
    if (s) { setShown(s); requestAnimationFrame(() => setOpen(true)); } else setOpen(false);
  }, [s]);
  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [onClose]);
  const key = shown ? `${shown.market}:${shown.coin}` : '';
  useEffect(() => {
    if (!shown) return;
    let live = true;
    setChart(null); setChartErr(null);
    sigenApi.chart(shown.market, shown.coin).then(a => live && setChart(a)).catch(e => live && setChartErr(message(e)));
    return () => { live = false; };
  }, [key]); // eslint-disable-line react-hooks/exhaustive-deps
  const levels = useMemo<Level[]>(() => {
    const t = shown;
    if (!t) return [];
    const l: Level[] = [];
    if (t.entry !== null) l.push({ price: t.entry, label: t.state === 'armed' ? 'Entry if it closes here' : 'Entry', tone: 'primary', dashed: t.state === 'armed' });
    if (t.stop !== null && t.state !== 'exit') l.push({ price: t.stop, label: 'Stop-loss', tone: 'down' });
    if (t.target !== null && t.state !== 'exit') l.push({ price: t.target, label: 'Take-profit', tone: 'up' });
    if (t.exit_price) l.push({ price: t.exit_price, label: 'Close', tone: 'faint' });
    return l;
  }, [shown]);
  if (!shown) return null;
  const t = shown;
  const c = t.confidence.parts;
  const aiShare = Math.round(c.ai_weight * 30);
  const k = sideOf(t);
  const up = k !== 'short';
  return (
    <>
      <div className="sheet-scrim" data-open={open} onClick={onClose} />
      <aside className="sheet" data-open={open} role="dialog" aria-modal="true" aria-label={`${t.coin} signal`}
        onTransitionEnd={() => !open && setShown(null)}>
        <div className="sheet-head">
          <Coin symbol={t.symbol} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="t-title">{t.coin} <DirBadge s={t} /></div>
            <div className="t-small muted">{t.market === 'spot' ? 'Spot' : 'Futures'} · {strategyName(t.strategy)} · checks every 4 hours</div>
          </div>
          <StateChip s={t} />
          <Btn kind="ghost" iconOnly icon="close" title="Close" onClick={onClose} />
        </div>
        <div className="sheet-body">
          <section className={`sg-hero ${t.state === 'exit' ? 'exit' : k === 'short' ? 'short' : k === 'none' ? 'none' : 'long'}`}>
            <div className="sg-side"><DirBadge s={t} big /><span className="hint">{SIDE[k].hint}</span></div>
            <p className="sg-instruction">{t.instruction}</p>
            <Plan s={t} />
            <div className="sg-scores">
              <ConfidenceMeter c={t.confidence} big />
              <PastRecord a={t.accuracy} />
            </div>
          </section>

          <section>
            <h4 className="t-title" style={{ marginBottom: 8 }}>The chart</h4>
            {chartErr && <div className="banner bad"><Icon name="cloud_off" /><div className="grow">{chartErr}</div></div>}
            {!chart && !chartErr && <Skeleton h={340} r={12} />}
            {chart && <div className="panel" style={{ overflow: 'hidden' }}><PriceChart a={chart} levels={levels} height={340} /></div>}
            <p className="t-small faint" style={{ marginTop: 6 }}>Each candle is 4 hours. Latest close {price(t.price)} (real OKX prices, not demo). Next check {until(t.next_decision, now)}.</p>
          </section>

          <section className="tonal side-col">
            <h4><Icon name="checklist" />{t.state === 'armed' || t.state === 'watching' ? 'What SiGen is waiting for' : t.checks_at === 'entry' ? 'Why it opened this trade' : 'Why this signal'}</h4>
            {t.checks_at === 'entry' && <p className="muted t-small" style={{ marginBottom: 6 }}>These were the conditions on the entry candle, {time(t.signal_time)}.</p>}
            {t.checks.length ? <Checklist checks={t.checks} /> : <p className="muted">{t.headline}</p>}
            <p className="muted t-small" style={{ marginTop: 6 }}><b>The strategy:</b> {t.rule}</p>
          </section>

          <section className="tonal side-col">
            <h4><Icon name="logout" />How to close the trade</h4>
            <ul className="sg-exit">
              {t.stop !== null && t.state !== 'exit' && <li><b>Stop-loss at {price(t.stop)}.</b> If the price {up ? 'falls' : 'rises'} to this, close the trade to limit the loss. Set it on the exchange when you open the trade.{t.initial_stop && t.initial_stop !== t.stop ? ` It started at ${price(t.initial_stop)} and has been moved to protect profit.` : ''}</li>}
              {t.target !== null && t.state !== 'exit' && <li><b>Take-profit at {price(t.target)}.</b> If the price {up ? 'rises' : 'falls'} to this, close the trade and keep the profit.</li>}
              {t.exit_rule && <li><b>Or when SiGen says close.</b> That happens on {t.exit_rule}.</li>}
              {t.trail && <li><b>Protecting profit.</b> {t.trail}</li>}
              <li>SiGen checks at every 4-hour close. When it is time to close, this signal changes to "Close now".</li>
            </ul>
          </section>

          <RegimeSection s={t} />

          <section className="tonal side-col">
            <h4><Icon name="psychology" />How sure is SiGen?</h4>
            <div className="sg-why">
              <div><span className="k">Reliability of past results</span><span className="v num">{Math.round(c.edge_certainty * 100)}%</span>
                <p>SiGen reshuffled its {t.accuracy.trades} past trades 2,000 times; this share of the reshuffles still made money. Counts for half of the confidence.</p></div>
              <div><span className="k">Profitable test periods</span><span className="v num">{c.folds_positive} of 4</span>
                <p>Each period is about 7 months the strategy was not tuned on. Counts for a fifth of the confidence.</p></div>
              <div><span className="k">The AI's view</span><span className="v num">{t.ai.p_win !== null ? `${Math.round(t.ai.p_win * 100)}%` : '—'}</span>
                <p>The AI's estimate that this trade wins, against {Math.round(t.ai.base_rate * 100)}% for this strategy on average.
                  {' '}It counts for only {aiShare}% of the confidence, because so far it has been {t.ai.holdout_auc > 0.52 ? 'only a little' : 'barely'} better than a coin flip at telling winners from losers.</p>
                {t.ai.drivers && t.ai.drivers.length > 0 && (
                  <div className="sg-drivers">{t.ai.drivers.map(d => (
                    <span key={d.feature} className={`sg-driver ${d.effect}`} title={d.effect === 'for' ? 'Counts in favour' : 'Counts against'}><Icon name={d.effect === 'for' ? 'add' : 'remove'} />{d.feature}</span>
                  ))}</div>
                )}
              </div>
            </div>
            {t.ai.unusual && <div className="banner warn" style={{ marginTop: 10 }}><Icon name="warning" /><div className="grow">Today's market looks unlike anything the AI learned from, so its view is less reliable. Confidence was cut by a quarter.</div></div>}
          </section>

          <section>
            <h4 className="t-title" style={{ marginBottom: 8 }}>Past record ({span(t.accuracy.history_days)} of price history)</h4>
            {(t.accuracy.history_days ?? 1095) < 700 && <div className="banner warn" style={{ marginBottom: 10 }}><Icon name="history" /><div className="grow">{t.coin} has only {span(t.accuracy.history_days)} of price history on OKX, so this record covers fewer kinds of market than the 3 years used for older coins.</div></div>}
            <div className="facts three num panel" style={{ overflow: 'hidden' }}>
              <div className="fact"><div className="k">Trades won</div><div className="v">{t.accuracy.win_rate_pct.toFixed(1)}%</div><div className="t-small faint">{t.accuracy.expected_win_rate_pct.toFixed(1)}% after allowing for luck</div></div>
              <div className="fact"><div className="k">Past trades</div><div className="v">{t.accuracy.trades}</div><div className="t-small faint">on prices it wasn't tuned on</div></div>
              <div className="fact"><div className="k">Won per $1 lost</div><div className="v">${t.accuracy.profit_factor.toFixed(2)}</div><div className="t-small faint">above $1 means it made money</div></div>
              <div className="fact"><div className="k">Average win</div><div className="v up">{timesRisk(t.accuracy.avg_win_r)}</div></div>
              <div className="fact"><div className="k">Average loss</div><div className="v down">{timesRisk(-t.accuracy.avg_loss_r)}</div></div>
              <div className="fact"><div className="k">Worst drop</div><div className="v">{t.accuracy.max_drawdown_pct.toFixed(1)}%</div><div className="t-small faint">of the account, risking {t.market === 'spot' ? '1%' : '2%'} per trade</div></div>
            </div>
            <p className="t-small faint" style={{ marginTop: 6 }}><b>Risk</b> is what you would lose if the stop-loss is hit. A win of 2× risk means you made twice that amount. Past results do not guarantee future ones.</p>
          </section>

          <p className="sg-disclaimer"><Icon name="info" />SiGen signals are generated by AI and automated rules and can be wrong. They are not financial advice. TradePilot LLC takes no responsibility for losses from acting on them.</p>
        </div>
      </aside>
    </>
  );
}

/* ---------- method + scan ---------- */

function ScanProgress({ scan }: { scan: SigenStatus['scan'] }) {
  const pct = scan.total ? Math.round(((scan.done || 0) / scan.total) * 100) : 0;
  return (
    <div className="sg-progress" aria-live="polite">
      <div className="t-small"><b>{scan.step || 'Starting'}</b>{scan.total ? ` · ${scan.done} of ${scan.total}` : ''}{scan.coin ? ` · ${scan.coin}` : ''}</div>
      <div className="meter"><span style={{ width: `${pct}%`, background: 'var(--primary)' }} /></div>
    </div>
  );
}

function RegimeStep({ ev }: { ev: SigenStatus['regime'] }) {
  if (!ev) return null;
  const v = ev.validation;
  return (
    <li><Icon name="waves" /><div><b>Choppy-market filter: {ev.enabled ? 'on' : 'off'}.</b>{' '}
      {ev.enabled && ev.rule ? `Trend signals are skipped when ${ruleText(ev.rule)}.` : <>
        The idea was to skip trend signals when prices are moving sideways. It was tested on {ev.trades.toLocaleString()} past signals: set up on the ones before {new Date(ev.calibrate_until).toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' })}, then checked on the {v?.all.trades.toLocaleString()} after.
        {v && <> It made results worse. The signals it would have skipped did better ({timesRisk(v.held_back.avg_r)} on average) than the ones it kept ({timesRisk(v.kept.avg_r)}), because big moves often start from quiet, sideways markets.</>}
        {ev.replay && <> On the last 30 days alone it would have looked helpful, which is why a single month can't prove a filter.</>}
        {ev.shadow && <> A version is being tried out on live signals: they are marked, not skipped, until there is enough new evidence.</>}
      </>}
    </div></li>
  );
}

function MethodPanel({ data, status, onTerms }: { data?: SigenSignals; status: SigenStatus; onTerms: () => void }) {
  const m = data?.model;
  return (
    <section className="panel">
      <div className="panel-head"><div><h3>How SiGen works</h3><div className="sub">Rebuilt on every scan from 3 years of 4-hour candles</div></div></div>
      <div className="panel-body sg-method">
        <ul className="sg-steps">
          <li><Icon name="leaderboard" /><div><b>Which coins.</b> The 25 largest coins by total value (ranked by {data?.universe_source || 'CoinGecko market cap'}) that OKX lets you trade both directly (spot) and as futures. Stablecoins and gold tokens are left out.</div></li>
          <li><Icon name="science" /><div><b>How strategies are tested.</b> Every strategy is tested on each coin's price history, including trading fees. It is tuned on older prices, then scored on the next 7 months it has not seen, four times over. A coin only gets signals from a strategy that made money in at least 3 of those 4 periods, over at least 30 trades, winning at least $1.20 for every $1 lost.</div></li>
          <li><Icon name="psychology" /><div><b>The AI.</b> It learns from {m ? m.trained_on.toLocaleString() : 'every'} past trades on {m?.coins ?? 25} coins which market conditions came before wins. It also warns when today's market looks unlike anything it learned from.</div></li>
          <RegimeStep ev={status.regime} />
          <li><Icon name="speed" /><div><b>Confidence</b> (0–100) shows how strong the evidence behind a signal is: 80 or more is High, 60 to 79 Medium, below 60 Low. It is not the chance of winning. Many of these strategies win fewer than half their trades and make money because their wins are bigger than their losses, so even High-confidence signals often lose. "Past record" shows how often they won.</div></li>
          <li><Icon name="schedule" /><div><b>When signals change.</b> Every 4 hours, when a candle closes, SiGen checks every coin again: new trades to open, open trades to keep, and trades to close.</div></li>
        </ul>
        {m && (
          <div className="sg-model">
            <h4 className="t-title-s">How the AI has done</h4>
            <p className="t-small muted">On the {m.holdout.trades.toLocaleString()} most recent trades it had never seen, it picked the winner over the loser {Math.round(m.holdout.auc * 100)}% of the time. A coin flip would score 50%. So it counts for only {Math.round(Math.min(1, Math.max(0, (m.holdout.auc - 0.5) / 0.1)) * 30)}% of the confidence score.</p>
            <table className="data sg-calib num">
              <thead><tr><th>AI expected to win</th><th className="r">Actually won</th><th className="r">Trades</th></tr></thead>
              <tbody>{m.holdout.calibration.map(r => (
                <tr key={r.predicted}><td>{Math.round(r.predicted * 100)}%</td><td className="r">{Math.round(r.actual * 100)}%</td><td className="r faint">{r.trades}</td></tr>
              ))}</tbody>
            </table>
          </div>
        )}
        <div className="sg-signed t-small muted">
          <Icon name="verified_user" />
          <span>Terms accepted by <b>{status.terms.name}</b> on {time(status.terms.accepted_at)} (version {status.terms.version}).</span>
          <Btn kind="text" small onClick={onTerms}>Read the terms</Btn>
        </div>
      </div>
    </section>
  );
}

/* ---------- page ---------- */

export function Sigen({ route, go, now }: { route: Extract<Route, { page: 'sigen' }>; go: (r: Route) => void; now: number }) {
  const market: SigenMarket = route.market || 'futures';
  const { status, data, err, loading, loadStatus, loadSignals } = useSigen(market);
  const [scanBusy, setScanBusy] = useState(false);
  const [termsOpen, setTermsOpen] = useState(false);
  const signals = data?.signals || [];
  const selected = signals.find(s => s.coin === route.coin) || null;
  const open = (s: Signal) => go({ page: 'sigen', market, coin: s.coin });

  if (!status) {
    return err
      ? <div className="banner bad"><Icon name="cloud_off" /><div className="grow">Can't load SiGen: {err}</div><div className="actions"><Btn kind="text" small onClick={loadStatus}>Retry</Btn></div></div>
      : <Skeleton h={420} r={16} />;
  }
  if (!status.terms.accepted) return <TermsGate terms={status.terms_text} onAccepted={loadStatus} />;

  const tabs = (
    <div className="sg-tabs">
      <Segmented<'live' | 'history'> label="SiGen view" value={route.view === 'history' ? 'history' : 'live'}
        onChange={v => go(v === 'history' ? { page: 'sigen', view: 'history' } : { page: 'sigen', market })}
        options={[{ value: 'live', label: 'Live signals' }, { value: 'history', label: 'Signal history' }]} />
    </div>
  );
  if (route.view === 'history') {
    return <div className="grid" style={{ gap: 16 }}>{tabs}<SigenHistory route={route} go={go} now={now} /></div>;
  }

  const scan = status.scan;
  const running = scan.state === 'running';
  const startScan = async () => {
    setScanBusy(true);
    const r = await sigenApi.scan();
    setScanBusy(false);
    if (r.ok) toast.success(r.message); else toast.error(r.message);
    loadStatus();
  };

  const act = signals.filter(s => s.state === 'entry' || s.state === 'exit');
  const inPlay = signals.filter(s => s.state === 'holding');
  const armed = signals.filter(s => s.state === 'armed')
    .sort((a, b) => Math.abs((a.entry ?? a.price) / a.price - 1) - Math.abs((b.entry ?? b.price) / b.price - 1));
  const watching = signals.filter(s => s.state === 'watching');
  const held = signals.filter(s => s.state === 'held');

  return (
    <div className="grid" style={{ gap: 16 }}>
      {tabs}
      <section className="panel sg-bar">
        <Segmented<SigenMarket> label="Market" value={market} onChange={m => go({ page: 'sigen', market: m })}
          options={[{ value: 'futures', label: 'Futures' }, { value: 'spot', label: 'Spot' }]} />
        <div className="sg-bar-text t-small muted">
          {running ? <ScanProgress scan={scan} />
            : status.generated_at ? <>{status.coins.length} coins tested {ago(status.generated_at, now)} · {data ? `${signals.length} have a strategy that passed` : 'loading signals…'}{signals[0] ? ` · prices as of ${clock(new Date(new Date(signals[0].bar_time).getTime() + 4 * 3600e3).toISOString())} ${tzName()}` : ''}</>
              : 'No scan yet'}
          {scan.state === 'error' && <span className="down"> · Last scan failed: {scan.error}</span>}
        </div>
        <span className="grow" />
        <Btn kind="tonal" icon="refresh" small busy={loading} disabled={!status.generated_at} onClick={() => loadSignals(market)} title="Re-read the latest candles">Refresh</Btn>
        <Btn kind="outlined" icon="radar" small busy={scanBusy} disabled={running} onClick={startScan} title="Re-test every strategy on every coin and retrain the AI (a few minutes)">{running ? 'Scanning…' : 'Rescan'}</Btn>
      </section>

      {err && status.generated_at && <div className="banner bad"><Icon name="cloud_off" /><div className="grow">{err}</div><div className="actions"><Btn kind="text" small onClick={() => loadSignals(market)}>Retry</Btn></div></div>}

      {!status.generated_at ? (
        <section className="panel">
          <Empty icon="radar" title={running ? 'The first scan is running' : 'Run the first scan'}>
            {running ? 'Testing every strategy on the 25 largest coins and training the AI. This takes a few minutes; signals appear here when it finishes.'
              : 'SiGen tests every strategy on the 25 largest coins and trains its AI before showing any signal. It takes a few minutes.'}
          </Empty>
          {!running && <div style={{ display: 'grid', justifyItems: 'center', paddingBottom: 28 }}><Btn icon="radar" busy={scanBusy} onClick={startScan}>Start the scan</Btn></div>}
        </section>
      ) : !data ? (
        <div className="sg-grid"><Skeleton h={340} r={28} /><Skeleton h={340} r={28} /></div>
      ) : (
        <>
          <section>
            <h3 className="sg-h">Act now <span className="count num">{act.length}</span><span className="sub">Trades to open or close at this 4-hour close</span></h3>
            {act.length ? (
              <div className="sg-grid">{act.map(s => <SignalTicket key={s.id} s={s} now={now} onOpen={() => open(s)} />)}</div>
            ) : (
              <p className="sg-quiet muted"><Icon name="check_circle" />Nothing to open or close right now. SiGen checks again {signals[0] ? `${until(signals[0].next_decision, now)}, at ${clock(signals[0].next_decision)} ${tzName()}` : 'at the next 4-hour close'}.</p>
            )}
          </section>

          {inPlay.length > 0 && (
            <section>
              <h3 className="sg-h">Open trades <span className="count num">{inPlay.length}</span><span className="sub">Already running. Keep the stop-loss in place until SiGen says close.</span></h3>
              <div className="sg-grid">{inPlay.map(s => <SignalTicket key={s.id} s={s} now={now} onOpen={() => open(s)} />)}</div>
            </section>
          )}

          {armed.length > 0 && (
            <section className="panel">
              <div className="panel-head"><div><h3>Possible trades <span className="count num">{armed.length}</span></h3><div className="sub">Not yet. Each one starts only if the 4-hour candle closing at {armed[0] ? `${clock(armed[0].valid_until)} ${tzName(new Date(armed[0].valid_until))}` : 'the next close'} ends past its entry price. Closest first.</div></div></div>
              <ArmedTable rows={armed} onOpen={open} selected={route.coin} />
            </section>
          )}

          {held.length > 0 && (
            <section className="panel">
              <div className="panel-head"><div><h3>Skipped: market too choppy <span className="count num">{held.length}</span></h3><div className="sub">Trend signals SiGen leaves out while prices are moving sideways</div></div></div>
              <ArmedTable rows={held} onOpen={open} selected={route.coin} />
            </section>
          )}

          {(watching.length > 0 || data.untested.length > 0) && (
            <section className="panel">
              <div className="panel-head"><div><h3>No trade</h3><div className="sub">Coins with no setup right now, and coins no strategy passed testing on</div></div></div>
              <div className="sg-rest">
                {watching.map(s => (
                  <button key={s.id} type="button" className="sg-rest-row" onClick={() => open(s)}>
                    <Coin symbol={s.symbol} />
                    <div><b>{s.coin}</b> <span className="muted">· {strategyName(s.strategy)}</span><div className="t-small faint">No setup yet. Waiting for {Object.values(s.trigger)[0]}</div></div>
                    <span className={`sg-score ${s.confidence.label.toLowerCase()}`}>{s.confidence.score}</span>
                  </button>
                ))}
                {data.untested.map(u => (
                  <div key={u.coin} className="sg-rest-row off">
                    <Coin symbol={`${u.coin}/USDT`} />
                    <div><b>{u.coin}</b> <span className="muted">· no signals</span>
                      <div className="t-small faint">{u.reason === 'no strategy passed testing' ? 'No strategy made money reliably on this coin' : u.reason[0].toUpperCase() + u.reason.slice(1)}{u.closest ? `. Closest was ${strategyName(u.closest.strategy)}: $${u.closest.profit_factor} won per $1 lost over ${u.closest.trades} trades, profitable in ${u.closest.folds_positive} of 4 periods.` : '.'}</div></div>
                  </div>
                ))}
              </div>
            </section>
          )}

          <MethodPanel data={data} status={status} onTerms={() => setTermsOpen(true)} />
          <p className="sg-disclaimer"><Icon name="info" />SiGen signals are generated by AI and automated rules and can be wrong. They are not financial advice. TradePilot LLC takes no responsibility for losses from acting on them.</p>
        </>
      )}

      <SignalSheet s={selected} now={now} onClose={() => go({ page: 'sigen', market })} />
      <Dialog open={termsOpen} onClose={() => setTermsOpen(false)} icon="gavel" title={status.terms_text.title}
        actions={<Btn kind="text" onClick={() => setTermsOpen(false)}>Close</Btn>}>
        <TermsText terms={status.terms_text} />
      </Dialog>
    </div>
  );
}
