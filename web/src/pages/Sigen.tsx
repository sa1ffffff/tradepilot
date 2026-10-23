import { useCallback, useEffect, useMemo, useState } from 'react';
import { toast } from 'sonner';
import { sigenApi, type Analysis, type Signal, type SigenMarket, type SigenSignals, type SigenStatus, type SigenTerms } from '../lib/api';
import type { Route } from '../lib/store';
import { ago, price, strategyName, time, until } from '../lib/format';
import { PriceChart, type Level } from '../components/PriceChart';
import { Checklist } from '../components/Thinking';
import { Btn, Chip, Coin, Dialog, Empty, Icon, Segmented, SideTag, Skeleton } from '../components/ui';
import '../sigen.css';

const visible = () => document.visibilityState === 'visible';
const message = (e: unknown) => (e instanceof Error ? e.message : String(e));
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
  entry: { label: 'Act now', icon: 'bolt', tone: 'info' },
  exit: { label: 'Exit now', icon: 'logout', tone: 'warn' },
  holding: { label: 'In play', icon: 'trending_up', tone: 'ok' },
  armed: { label: 'Waiting for trigger', icon: 'hourglass_top', tone: '' },
  watching: { label: 'Watching', icon: 'visibility', tone: '' }
};

function StateChip({ s }: { s: Signal }) {
  const m = STATE[s.state];
  return <Chip tone={m.tone} icon={m.icon}>{m.label}</Chip>;
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

function Accuracy({ a }: { a: Signal['accuracy'] }) {
  return (
    <div className="sg-acc">
      <div className="k">Accuracy</div>
      <div className="v num">{a.win_rate_pct.toFixed(0)}%<span className="of">wins</span></div>
      <div className="t-small muted num">{a.trades} tested trades · avg win {a.avg_win_r.toFixed(1)}R, loss {a.avg_loss_r.toFixed(1)}R</div>
    </div>
  );
}

function Levels({ s }: { s: Signal }) {
  const cells: { k: string; v: string; d?: string; tone?: string }[] = [];
  if (s.state === 'exit') {
    cells.push({ k: 'Entry', v: price(s.entry), d: time(s.signal_time) });
    cells.push({ k: 'Exit', v: price(s.exit_price), d: 'latest close', tone: 'primary' });
    cells.push({ k: 'Result', v: `${(s.result_r ?? 0) > 0 ? '+' : ''}${(s.result_r ?? 0).toFixed(2)}R`, tone: (s.result_r ?? 0) > 0 ? 'up' : 'down', d: 'of the amount risked' });
  } else if (s.entry !== null) {
    cells.push({ k: s.state === 'armed' ? 'Entry trigger' : 'Entry', v: price(s.entry), d: s.state === 'holding' ? time(s.signal_time) : s.state === 'armed' ? `${pctFrom(s.entry, s.price)} from now` : 'at the latest close' });
    if (s.stop !== null) cells.push({ k: s.state === 'holding' ? 'Stop-loss now' : 'Stop-loss', v: price(s.stop), d: `${pctFrom(s.stop, s.state === 'armed' ? s.entry : s.price)} ${s.state === 'armed' ? 'from entry' : 'from now'}`, tone: 'down' });
    cells.push(s.target !== null
      ? { k: 'Take profit', v: price(s.target), d: `${pctFrom(s.target, s.state === 'armed' ? s.entry : s.price)} ${s.state === 'armed' ? 'from entry' : 'from now'}`, tone: 'up' }
      : { k: 'Exit', v: 'Exit rule', d: s.trail ? 'no fixed target; stop trails' : 'no fixed target' });
  }
  if (!cells.length) return null;
  return (
    <div className="sg-levels num">
      {cells.map(c => (
        <div key={c.k} className={c.tone || ''}>
          <div className="k">{c.k}</div>
          <div className="v">{c.v}</div>
          {c.d && <div className="d">{c.d}</div>}
        </div>
      ))}
    </div>
  );
}

function SignalTicket({ s, onOpen, now }: { s: Signal; onOpen: () => void; now: number }) {
  const dir = s.state === 'exit' ? 'exit' : s.direction === 'short' ? 'short' : 'long';
  return (
    <button type="button" className={`sg-ticket ${dir} ${s.state}`} onClick={onOpen}>
      <div className="sg-ticket-top">
        <Coin symbol={s.symbol} size={40} />
        <div className="who">
          <div className="t-title">{s.coin}</div>
          <div className="t-small muted">{s.market === 'spot' ? 'Spot' : 'Perpetual'} · {s.timeframe} · {strategyName(s.strategy)}</div>
        </div>
        <StateChip s={s} />
      </div>
      <div className="sg-action"><Icon name={dir === 'exit' ? 'logout' : dir === 'short' ? 'south_east' : 'north_east'} />{s.action}</div>
      <p className="sg-instruction">{s.instruction}</p>
      <Levels s={s} />
      <div className="sg-scores">
        <ConfidenceMeter c={s.confidence} />
        <Accuracy a={s.accuracy} />
      </div>
      <div className="sg-ticket-foot t-small muted">
        <span><Icon name="schedule" />{s.state === 'entry' ? `Valid until the next close, ${until(s.next_decision, now)}` : `Next check ${until(s.next_decision, now)}`}</span>
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
          <tr><th>Coin</th><th>Signal</th><th className="r">Entry trigger</th><th className="r hide-sm">Stop-loss</th><th className="r hide-sm">Take profit</th><th className="r">Confidence</th><th className="r hide-sm">Accuracy</th></tr>
        </thead>
        <tbody>
          {rows.map(s => (
            <tr key={s.id} className="clickable" tabIndex={0} aria-selected={s.coin === selected}
              onClick={() => onOpen(s)} onKeyDown={e => e.key === 'Enter' && onOpen(s)}>
              <td><div className="sym"><Coin symbol={s.symbol} /><div><div className="name">{s.coin}</div><div className="meta">{strategyName(s.strategy)}</div></div></div></td>
              <td>{s.direction && <SideTag side={s.direction} />} <span className="muted">if a close {s.entry !== null && s.entry < s.price ? 'below' : 'above'}</span></td>
              <td className="r num">{price(s.entry)}<div className="t-small faint">{s.entry !== null ? pctFrom(s.entry, s.price) : ''}</div></td>
              <td className="r num hide-sm down">{price(s.stop)}</td>
              <td className="r num hide-sm">{s.target !== null ? <span className="up">{price(s.target)}</span> : <span className="faint">exit rule</span>}</td>
              <td className="r num"><span className={`sg-score ${s.confidence.label.toLowerCase()}`}>{s.confidence.score}</span></td>
              <td className="r num hide-sm">{s.accuracy.win_rate_pct.toFixed(0)}% <span className="faint">of {s.accuracy.trades}</span></td>
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
    if (t.entry !== null) l.push({ price: t.entry, label: t.state === 'armed' ? 'Entry trigger' : 'Entry', tone: 'primary', dashed: t.state === 'armed' });
    if (t.stop !== null && t.state !== 'exit') l.push({ price: t.stop, label: 'Stop-loss', tone: 'down' });
    if (t.target !== null && t.state !== 'exit') l.push({ price: t.target, label: 'Take profit', tone: 'up' });
    if (t.exit_price) l.push({ price: t.exit_price, label: 'Exit', tone: 'faint' });
    return l;
  }, [shown]);
  if (!shown) return null;
  const t = shown;
  const c = t.confidence.parts;
  const aiShare = Math.round(c.ai_weight * 30);
  return (
    <>
      <div className="sheet-scrim" data-open={open} onClick={onClose} />
      <aside className="sheet" data-open={open} role="dialog" aria-modal="true" aria-label={`${t.coin} signal`}
        onTransitionEnd={() => !open && setShown(null)}>
        <div className="sheet-head">
          <Coin symbol={t.symbol} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="t-title">{t.coin} {t.direction && <SideTag side={t.direction} />}</div>
            <div className="t-small muted">{t.market === 'spot' ? 'Spot' : 'Perpetual futures'} · {t.timeframe} · {strategyName(t.strategy)}</div>
          </div>
          <StateChip s={t} />
          <Btn kind="ghost" iconOnly icon="close" title="Close" onClick={onClose} />
        </div>
        <div className="sheet-body">
          <section className={`sg-hero ${t.state === 'exit' ? 'exit' : t.direction || 'long'}`}>
            <div className="sg-action big"><Icon name={t.state === 'exit' ? 'logout' : t.direction === 'short' ? 'south_east' : 'north_east'} />{t.action}</div>
            <p className="sg-instruction">{t.instruction}</p>
            <Levels s={t} />
            <div className="sg-scores">
              <ConfidenceMeter c={t.confidence} big />
              <Accuracy a={t.accuracy} />
            </div>
          </section>

          <section>
            <h4 className="t-title" style={{ marginBottom: 8 }}>The chart</h4>
            {chartErr && <div className="banner bad"><Icon name="cloud_off" /><div className="grow">{chartErr}</div></div>}
            {!chart && !chartErr && <Skeleton h={340} r={12} />}
            {chart && <div className="panel" style={{ overflow: 'hidden' }}><PriceChart a={chart} levels={levels} height={340} /></div>}
            <p className="t-small faint" style={{ marginTop: 6 }}>Last close {price(t.price)}, from the 4h candle that opened {time(t.bar_time)} (OKX market prices, not demo). Next decision {until(t.next_decision, now)}.</p>
          </section>

          <section className="tonal side-col">
            <h4><Icon name="login" />{t.state === 'armed' || t.state === 'watching' ? 'What it is waiting for' : t.checks_at === 'entry' ? 'Why it entered' : 'Why this signal'}</h4>
            {t.checks_at === 'entry' && <p className="muted t-small" style={{ marginBottom: 6 }}>The conditions on the entry candle, {time(t.signal_time)}.</p>}
            {t.checks.length ? <Checklist checks={t.checks} /> : <p className="muted">{t.headline}</p>}
            <p className="muted t-small" style={{ marginTop: 6 }}>{t.rule}</p>
          </section>

          <section className="tonal side-col">
            <h4><Icon name="logout" />When to exit</h4>
            <ul className="sg-exit">
              {t.stop !== null && t.state !== 'exit' && <li><b>Stop-loss</b> at {price(t.stop)}{t.initial_stop && t.initial_stop !== t.stop ? ` (started at ${price(t.initial_stop)})` : ''}. Exit at once if price trades through it.</li>}
              {t.target !== null && t.state !== 'exit' && <li><b>Take profit</b> at {price(t.target)}.</li>}
              {t.exit_rule && <li><b>Exit rule:</b> close the trade on {t.exit_rule}.</li>}
              {t.trail && <li><b>Trailing stop:</b> {t.trail}</li>}
              <li>SiGen re-checks on every 4h close and shows "Exit now" when the rule fires.</li>
            </ul>
          </section>

          <section className="tonal side-col">
            <h4><Icon name="psychology" />How confident, and why</h4>
            <div className="sg-why">
              <div><span className="k">Edge certainty</span><span className="v num">{Math.round(c.edge_certainty * 100)}%</span>
                <p>Of 2,000 reshuffles of its {t.accuracy.trades} tested trades, this share still made money. Half the score.</p></div>
              <div><span className="k">Consistency</span><span className="v num">{c.folds_positive} of 4</span>
                <p>Test periods (each about 7 months, never used to tune it) that ended in profit. A fifth of the score.</p></div>
              <div><span className="k">AI read of this setup</span><span className="v num">{t.ai.p_win !== null ? `${Math.round(t.ai.p_win * 100)}%` : '—'}</span>
                <p>The model's win chance for this setup, against {Math.round(t.ai.base_rate * 100)}% for this strategy on average.
                  {' '}It counts for {aiShare}% of the score, because on recent trades it hadn't seen it ranked setups {t.ai.holdout_auc >= 0.5 ? `${Math.round(t.ai.holdout_auc * 100)}% right (50% is a coin flip)` : 'no better than chance'}.</p>
                {t.ai.drivers && t.ai.drivers.length > 0 && (
                  <div className="sg-drivers">{t.ai.drivers.map(d => (
                    <span key={d.feature} className={`sg-driver ${d.effect}`}><Icon name={d.effect === 'for' ? 'add' : 'remove'} />{d.feature}</span>
                  ))}</div>
                )}
              </div>
            </div>
            {t.ai.unusual && <div className="banner warn" style={{ marginTop: 10 }}><Icon name="warning" /><div className="grow">Today's conditions are unlike anything the AI trained on (dissimilarity {t.ai.di?.toFixed(2)}), so its read is less reliable. Confidence is cut by a quarter.</div></div>}
          </section>

          <section>
            <h4 className="t-title" style={{ marginBottom: 8 }}>Track record (3 years, out of sample)</h4>
            <div className="facts three num panel" style={{ overflow: 'hidden' }}>
              <div className="fact"><div className="k">Win rate</div><div className="v">{t.accuracy.win_rate_pct.toFixed(1)}%</div><div className="t-small faint">{t.accuracy.expected_win_rate_pct.toFixed(1)}% after adjusting for selection</div></div>
              <div className="fact"><div className="k">Tested trades</div><div className="v">{t.accuracy.trades}</div></div>
              <div className="fact"><div className="k">Profit factor</div><div className="v">{t.accuracy.profit_factor.toFixed(2)}</div><div className="t-small faint">gross wins ÷ gross losses</div></div>
              <div className="fact"><div className="k">Average win</div><div className="v up">{t.accuracy.avg_win_r.toFixed(2)}R</div></div>
              <div className="fact"><div className="k">Average loss</div><div className="v down">{t.accuracy.avg_loss_r.toFixed(2)}R</div></div>
              <div className="fact"><div className="k">Worst drawdown</div><div className="v">{t.accuracy.max_drawdown_pct.toFixed(1)}%</div><div className="t-small faint">at {t.market === 'spot' ? '1%' : '2%'} risk per trade</div></div>
            </div>
            <p className="t-small faint" style={{ marginTop: 6 }}>R is the amount risked on a trade: from entry to the stop-loss. Historical results; future results will differ.</p>
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

function MethodPanel({ data, status, onTerms }: { data?: SigenSignals; status: SigenStatus; onTerms: () => void }) {
  const m = data?.model;
  return (
    <section className="panel">
      <div className="panel-head"><div><h3>How SiGen decides</h3><div className="sub">Rebuilt on every scan from 3 years of 4h candles</div></div></div>
      <div className="panel-body sg-method">
        <ul className="sg-steps">
          <li><Icon name="leaderboard" /><div><b>The coins.</b> The 25 largest (ranked by {data?.universe_source || 'CoinGecko market cap'}) that OKX lists as both spot and perpetual futures. Stablecoins and metal tokens are left out.</div></li>
          <li><Icon name="science" /><div><b>The test.</b> Every strategy the bots use runs a walk-forward test on each coin, with trading costs: tuned on the past, scored on the next 7 months, four times over. A coin gets signals only from a strategy that passes the bots' own bar: at least 30 trades, profit factor 1.2 or more, and 3 of 4 periods profitable.</div></li>
          <li><Icon name="psychology" /><div><b>The AI.</b> A model trained on {m ? m.trained_on.toLocaleString() : 'every'} tested trades across {m?.coins ?? 25} coins learns which conditions came before winners. A dissimilarity check flags markets it hasn't seen.</div></li>
          <li><Icon name="speed" /><div><b>Confidence</b> (0–100) is how strongly the evidence backs a signal: High is 80 or more, Medium 60 to 79. It is not a win chance. Most of these strategies win fewer than half their trades and make their money on larger wins, so even High signals lose often. Accuracy, next to it, is the win rate.</div></li>
          <li><Icon name="schedule" /><div><b>The signal.</b> On every closed 4h candle the strategy is replayed to the latest bar. That gives the action, stop-loss, target and exit rule.</div></li>
        </ul>
        {m && (
          <div className="sg-model">
            <h4 className="t-title-s">The AI's own track record</h4>
            <p className="t-small muted">Checked on the {m.holdout.trades.toLocaleString()} most recent trades it never trained on ({time(m.holdout.from, true)} to {time(m.holdout.to, true)}).
              {' '}Within a strategy it ranked winners above losers {Math.round(m.holdout.auc * 100)}% of the time (50% is a coin flip), so it counts for {Math.round(Math.min(1, Math.max(0, (m.holdout.auc - 0.5) / 0.1)) * 30)}% of the confidence score.</p>
            <table className="data sg-calib num">
              <thead><tr><th>AI's predicted win rate</th><th className="r">Actual</th><th className="r">Trades</th></tr></thead>
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

  return (
    <div className="grid" style={{ gap: 16 }}>
      <section className="panel sg-bar">
        <Segmented<SigenMarket> label="Market" value={market} onChange={m => go({ page: 'sigen', market: m })}
          options={[{ value: 'futures', label: 'Futures' }, { value: 'spot', label: 'Spot' }]} />
        <div className="sg-bar-text t-small muted">
          {running ? <ScanProgress scan={scan} />
            : status.generated_at ? <>Tested {status.coins.length} coins {ago(status.generated_at, now)} · {data ? `${signals.length} with a tested strategy` : 'loading signals…'}{data?.generated_at && signals[0] ? ` · candle ${time(signals[0].bar_time)}` : ''}</>
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
            <h3 className="sg-h">Act now <span className="count num">{act.length}</span></h3>
            {act.length ? (
              <div className="sg-grid">{act.map(s => <SignalTicket key={s.id} s={s} now={now} onOpen={() => open(s)} />)}</div>
            ) : (
              <p className="sg-quiet muted"><Icon name="check_circle" />Nothing to act on at this candle. SiGen checks again {signals[0] ? until(signals[0].next_decision, now) : 'at the next 4h close'}.</p>
            )}
          </section>

          {inPlay.length > 0 && (
            <section>
              <h3 className="sg-h">In play <span className="count num">{inPlay.length}</span><span className="sub">Signals already active; they hold until the stop or exit rule</span></h3>
              <div className="sg-grid">{inPlay.map(s => <SignalTicket key={s.id} s={s} now={now} onOpen={() => open(s)} />)}</div>
            </section>
          )}

          {armed.length > 0 && (
            <section className="panel">
              <div className="panel-head"><div><h3>Waiting for a trigger <span className="count num">{armed.length}</span></h3><div className="sub">Each becomes a signal if a 4h candle closes beyond its entry trigger. Closest first.</div></div></div>
              <ArmedTable rows={armed} onOpen={open} selected={route.coin} />
            </section>
          )}

          {(watching.length > 0 || data.untested.length > 0) && (
            <section className="panel">
              <div className="panel-head"><div><h3>No signal</h3><div className="sub">Coins waiting on an indicator, and coins where no strategy passed testing</div></div></div>
              <div className="sg-rest">
                {watching.map(s => (
                  <button key={s.id} type="button" className="sg-rest-row" onClick={() => open(s)}>
                    <Coin symbol={s.symbol} />
                    <div><b>{s.coin}</b> <span className="muted">· {strategyName(s.strategy)}</span><div className="t-small faint">Waiting on an indicator, not a price: {Object.values(s.trigger)[0]}</div></div>
                    <span className={`sg-score ${s.confidence.label.toLowerCase()}`}>{s.confidence.score}</span>
                  </button>
                ))}
                {data.untested.map(u => (
                  <div key={u.coin} className="sg-rest-row off">
                    <Coin symbol={`${u.coin}/USDT`} />
                    <div><b>{u.coin}</b> <span className="muted">· not covered</span>
                      <div className="t-small faint">{u.reason === 'no strategy passed testing' ? 'No strategy passed testing' : u.reason}{u.closest ? `. Closest: ${strategyName(u.closest.strategy)}, profit factor ${u.closest.profit_factor} over ${u.closest.trades} trades, ${u.closest.folds_positive} of 4 periods profitable.` : '.'}</div></div>
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
