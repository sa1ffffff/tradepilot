import { useState } from 'react';
import { toast } from 'sonner';
import { api, type BotName, type OverviewRow, type Status } from '../lib/api';
import type { Route } from '../lib/store';
import { ago, coin, price, time, tone, until, usd } from '../lib/format';
import { Btn, Dialog, Icon, Money } from './ui';

const NAMES: Record<BotName, string> = { spot: 'Spot bot', futures: 'Futures bot' };
const BOTS: BotName[] = ['spot', 'futures'];

export function useBotActions(refresh: () => void) {
  const [busy, setBusy] = useState<string | null>(null);
  const run = async (key: string, fn: () => Promise<{ ok: boolean; message: string; pending?: boolean }>) => {
    setBusy(key);
    try {
      const r = await fn();
      if (r.ok) (r.pending ? toast.info : toast.success)(r.message);
      else toast.error(r.message);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Request failed');
    } finally {
      setBusy(null);
      refresh();
    }
  };
  return { busy, run };
}

type StopAsk = { bot: BotName; force: boolean } | null;

/** Start / stop with a confirmation that says what happens to open positions. */
function useBotControl(status: Status, refresh: () => void) {
  const { busy, run } = useBotActions(refresh);
  const [confirm, setConfirm] = useState<StopAsk>(null);
  const [starting, setStarting] = useState<BotName | null>(null);
  const openOf = (bot: BotName) => status.positions.filter(p => p.bot === bot);
  const start = (bot: BotName) => setStarting(bot);
  const L = status.limits;
  const startSlots = starting ? status.slots.filter(s => s.bot === starting) : [];
  const dialog = (
    <>
    <Dialog
      open={!!starting}
      onClose={() => setStarting(null)}
      icon="play_circle"
      title={starting ? `Start the ${NAMES[starting].toLowerCase()}?` : ''}
      actions={<>
        <Btn kind="text" onClick={() => setStarting(null)}>Cancel</Btn>
        <Btn kind="filled" onClick={() => {
          const b = starting!;
          setStarting(null);
          run(`start-${b}`, () => api.startBot(b));
        }}>Start trading on demo</Btn>
      </>}
    >
      {starting && (
        <>
          <p>It places real orders on your OKX <b>demo</b> account whenever a strategy's conditions all hold on a closed candle.</p>
          <ul className="num">
            <li>{startSlots.length === 1 ? `${startSlots[0].symbol} ${startSlots[0].timeframe}` : `${startSlots.length} strategies: ${startSlots.map(s => coin(s.symbol)).join(', ')}`}</li>
            {starting === 'futures'
              ? <li>{(L.futures_risk * 100).toFixed(0)}% of equity risked per trade, up to {L.futures_max_leverage}× isolated, margin capped at {Math.round(L.futures_max_margin * 100)}%</li>
              : <li>Up to {usd(L.spot_max_notional)} per position</li>}
            <li>Stops for the day after losing {usd(starting === 'futures' ? L.futures_daily_loss : L.spot_daily_loss)}{status.target.daily_target_usd ? ` or making ${usd(status.target.daily_target_usd)}` : ''}</li>
            {status.kill_switch && <li>New entries are paused right now, so it will only manage exits until you resume.</li>}
          </ul>
        </>
      )}
    </Dialog>
    <Dialog
      open={!!confirm}
      onClose={() => setConfirm(null)}
      icon={confirm?.force ? 'dangerous' : 'stop_circle'}
      title={confirm ? `${confirm.force ? 'End' : 'Stop'} the ${NAMES[confirm.bot].toLowerCase()}?` : ''}
      actions={<>
        <Btn kind="text" onClick={() => setConfirm(null)}>Cancel</Btn>
        <Btn kind={confirm?.force ? 'danger' : 'filled'} onClick={() => {
          const c = confirm!;
          setConfirm(null);
          run(`stop-${c.bot}`, () => (c.force ? api.forceStopBot(c.bot) : api.stopBot(c.bot)));
        }}>{confirm?.force ? 'End process' : 'Stop bot'}</Btn>
      </>}
    >
      {confirm && (
        <>
          <p>{confirm.force
            ? 'This ends the process immediately, even mid-order. Use it only if a normal stop is stuck.'
            : 'It finishes its current check, then stops. No new trades are taken while it is stopped.'}</p>
          {openOf(confirm.bot).length > 0 && (
            <p>{confirm.bot === 'futures'
              ? `${openOf(confirm.bot).length} open position(s) keep their stop-loss resting on OKX, but the trailing stop and exit signals pause until you start it again.`
              : 'The open spot position has no stop on OKX: its stop is checked by the bot, so it is unprotected while the bot is stopped.'}</p>
          )}
        </>
      )}
    </Dialog>
    </>
  );
  return { busy, start, ask: setConfirm, dialog, openOf };
}

function isStale(b: Status['bots'][BotName], now: number) {
  return b.running && !!b.heartbeat && now - new Date(b.heartbeat).getTime() > (b.poll_seconds + 120) * 1000;
}

/** The nearest price trigger among a bot's strategies: what it is closest to doing. */
function closest(rows: OverviewRow[]) {
  let best: { row: OverviewRow; side: 'long' | 'short'; dist: number; level: number } | null = null;
  for (const row of rows) {
    for (const side of ['long', 'short'] as const) {
      const lv = row.sides?.[side]?.trigger_level;
      if (!lv || !row.close) continue;
      const dist = (lv / row.close - 1) * 100;
      if (!best || Math.abs(dist) < Math.abs(best.dist)) best = { row, side, dist, level: lv };
    }
  }
  return best;
}

/** The two bots, full width at the top of the Overview. */
export function BotHero({ status, overview, refresh, now, go }: {
  status: Status; overview: OverviewRow[] | null; refresh: () => void; now: number; go: (r: Route) => void;
}) {
  const { busy, start, ask, dialog, openOf } = useBotControl(status, refresh);
  return (
    <section className="bot-hero" aria-label="Bots">
      {BOTS.map(bot => {
        const b = status.bots[bot];
        const stale = isStale(b, now);
        const rows = (overview || []).filter(r => r.bot === bot);
        const slots = status.slots.filter(s => s.bot === bot);
        const open = openOf(bot);
        const unreal = open.reduce((s, p) => s + (p.unrealized || 0), 0);
        const next = rows.map(r => r.next_decision).filter(Boolean).sort()[0];
        const near = closest(rows);
        const signals = rows.filter(r => r.mood === 'signal').length;
        const state = b.running ? (stale ? 'stale' : 'on') : b.stop_pending ? 'stopping' : 'off';
        return (
          <article key={bot} className={`hero-card ${state}`}>
            <header className="hero-top">
              <span className="hero-avatar" aria-hidden>
                <Icon name={bot === 'spot' ? 'currency_bitcoin' : 'swap_vert'} />
              </span>
              <div className="hero-who">
                <h3>{NAMES[bot]}</h3>
                <div className="hero-state">
                  <span className={`dot ${state === 'on' ? 'on' : state === 'stale' ? 'warn' : 'off'}`} aria-hidden />
                  {state === 'on' ? `Running since ${time(b.since)}` : state === 'stale' ? 'Running, but no heartbeat lately'
                    : state === 'stopping' ? 'Stopping…' : b.last_stopped ? `Stopped ${ago(b.last_stopped, now)}` : 'Not started yet'}
                </div>
              </div>
              {b.running ? (
                <Btn kind="tonal" icon="stop_circle" busy={busy === `stop-${bot}`} onClick={() => ask({ bot, force: false })}>Stop</Btn>
              ) : (
                <Btn kind="filled" icon="play_arrow" busy={busy === `start-${bot}`} onClick={() => start(bot)}>Start</Btn>
              )}
            </header>

            <div className="hero-numbers">
              <div>
                <div className="k">Today, realized</div>
                <div className={`v ${tone(status.pnl.today[bot])}`}><Money value={status.pnl.today[bot]} /></div>
              </div>
              <div>
                <div className="k">{open.length ? `${open.length} open` : 'Positions'}</div>
                <div className={`v sm ${tone(unreal)}`}>{open.length ? usd(unreal, true) : 'Flat'}</div>
              </div>
              <div>
                <div className="k">{b.running ? 'Next decision' : 'Last ran'}</div>
                <div className="v sm">{b.running ? until(next, now) : b.last_stopped ? time(b.last_stopped) : '—'}</div>
              </div>
            </div>

            <div className="hero-thought">
              <Icon name={signals ? 'bolt' : open.length ? 'trending_up' : 'radar'} fill={!!signals} />
              <p>
                {open.length ? (
                  <>In {open.map(p => `${coin(p.symbol)} ${p.side}`).join(', ')}, stop{open.length > 1 ? 's' : ''} resting{bot === 'futures' ? ' on OKX' : ' in the bot'}.</>
                ) : signals ? (
                  <>Signal on the last candle for {rows.filter(r => r.mood === 'signal').map(r => coin(r.symbol)).join(', ')}.</>
                ) : near ? (
                  <>Closest to a trade: <b>{coin(near.row.symbol)} {near.side}</b> on a close {near.side === 'long' ? 'above' : 'below'} {price(near.level)} <span className="num">({near.dist > 0 ? '+' : '−'}{Math.abs(near.dist).toFixed(1)}%)</span>.</>
                ) : overview ? (
                  <>Every strategy is waiting on an indicator, not a price.</>
                ) : <>Reading the latest candles…</>}
                {!b.running && ' Not trading while stopped.'}
              </p>
            </div>

            <div className="hero-crew" aria-label={`${NAMES[bot]} strategies`}>
              {slots.map(s => {
                const mood = rows.find(r => r.symbol === s.symbol)?.mood;
                return (
                  <button key={s.symbol} className={`crew ${mood || ''}`} onClick={() => go({ page: 'strategies', bot, symbol: s.symbol })}
                    title={`${coin(s.symbol)} ${s.timeframe}: ${mood === 'holding' ? 'in a trade' : mood === 'signal' ? 'signal' : 'watching'}`}>
                    <span className="crew-dot" aria-hidden />{coin(s.symbol)}<span className="crew-tf">{s.timeframe}</span>
                  </button>
                );
              })}
            </div>

            {b.stop_pending && b.running && (
              <div className="t-small muted">
                Waiting for the current check to finish.{' '}
                <button className="btn text sm" onClick={() => ask({ bot, force: true })}>End it now</button>
              </div>
            )}
          </article>
        );
      })}
      {dialog}
    </section>
  );
}

/** Compact version for the Controls page. */
export function BotPanel({ status, refresh, now }: { status: Status; refresh: () => void; now: number }) {
  const { busy, start, ask, dialog, openOf } = useBotControl(status, refresh);
  const fut = status.slots.filter(s => s.bot === 'futures');
  const spot = status.slots.find(s => s.bot === 'spot');
  return (
    <section className="panel" aria-labelledby="bots-h">
      <div className="panel-head">
        <div>
          <h3 id="bots-h">Bots</h3>
          <div className="sub">Both trade your OKX demo account</div>
        </div>
      </div>
      <div className="bots">
        {BOTS.map(bot => {
          const b = status.bots[bot];
          const stale = isStale(b, now);
          const what = bot === 'spot'
            ? spot ? `${spot.symbol} ${spot.timeframe}` : 'No strategy file'
            : `${fut.length} strategies, ${fut.map(s => s.symbol.split('/')[0]).join(' · ')}`;
          return (
            <div className="bot" key={bot}>
              <div className="bot-top">
                <span className={`avatar${b.running ? ' on' : ''}`}><Icon name={bot === 'spot' ? 'currency_bitcoin' : 'swap_vert'} /></span>
                <div className="who">
                  <div className="t-title">
                    {NAMES[bot]}
                    <span className={`dot ${b.running ? (stale ? 'warn' : 'on') : 'off'}`} aria-hidden />
                  </div>
                  <div className="t-small muted">
                    {b.running ? (stale ? 'Running, but no heartbeat lately' : `Running since ${time(b.since)}`) :
                      b.stop_pending ? 'Stopping…' : `Stopped ${b.last_stopped ? ago(b.last_stopped, now) : ''}`}
                  </div>
                </div>
                {b.running ? (
                  <Btn kind="tonal" small icon="stop_circle" busy={busy === `stop-${bot}`} onClick={() => ask({ bot, force: false })}>Stop</Btn>
                ) : (
                  <Btn kind="filled" small icon="play_arrow" busy={busy === `start-${bot}`} onClick={() => start(bot)}>Start</Btn>
                )}
              </div>
              <div className="bot-facts">
                <span><Icon name="candlestick_chart" />{what}</span>
                <span><Icon name="account_balance_wallet" />{openOf(bot).length ? `${openOf(bot).length} open` : 'Flat'}</span>
                {b.running && b.heartbeat && <span><Icon name="favorite" />Checked {ago(b.heartbeat, now)}</span>}
              </div>
              {b.stop_pending && b.running && (
                <div className="t-small muted">
                  Waiting for the current check to finish.{' '}
                  <button className="btn text sm" onClick={() => ask({ bot, force: true })}>End it now</button>
                </div>
              )}
            </div>
          );
        })}
      </div>
      {dialog}
    </section>
  );
}
