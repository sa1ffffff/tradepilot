import { useState } from 'react';
import { toast } from 'sonner';
import { api, type BotName, type Status } from '../lib/api';
import { ago, time } from '../lib/format';
import { Btn, Dialog, Icon } from './ui';

const NAMES: Record<BotName, string> = { spot: 'Spot bot', futures: 'Futures bot' };

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

export function BotPanel({ status, refresh, now }: { status: Status; refresh: () => void; now: number }) {
  const { busy, run } = useBotActions(refresh);
  const [confirm, setConfirm] = useState<{ bot: BotName; force: boolean } | null>(null);
  const fut = status.slots.filter(s => s.bot === 'futures');
  const spot = status.slots.find(s => s.bot === 'spot');
  const openOf = (bot: BotName) => status.positions.filter(p => p.bot === bot);

  return (
    <section className="panel" aria-labelledby="bots-h">
      <div className="panel-head">
        <div>
          <h3 id="bots-h">Bots</h3>
          <div className="sub">Both trade your OKX demo account</div>
        </div>
      </div>
      <div className="bots">
        {(['spot', 'futures'] as BotName[]).map(bot => {
          const b = status.bots[bot];
          const stale = b.running && b.heartbeat && now - new Date(b.heartbeat).getTime() > (b.poll_seconds + 120) * 1000;
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
                  <Btn kind="tonal" small icon="stop_circle" busy={busy === `stop-${bot}`} onClick={() => setConfirm({ bot, force: false })}>Stop</Btn>
                ) : (
                  <Btn kind="filled" small icon="play_arrow" busy={busy === `start-${bot}`} onClick={() => run(`start-${bot}`, () => api.startBot(bot))}>Start</Btn>
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
                  <button className="btn text sm" onClick={() => setConfirm({ bot, force: true })}>End it now</button>
                </div>
              )}
            </div>
          );
        })}
      </div>
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
    </section>
  );
}
