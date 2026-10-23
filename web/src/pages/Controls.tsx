import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { api, type Assessment, type Status } from '../lib/api';
import type { ConsoleData } from '../lib/store';
import { time, usd } from '../lib/format';
import { BotPanel, useBotActions } from '../components/Bots';
import { Btn, Chip, Dialog, Icon, Skeleton, Switch } from '../components/ui';

const VERDICT = {
  realistic: { tone: 'ok', label: 'Realistic', color: 'var(--up)' },
  stretch: { tone: 'warn', label: 'A stretch', color: 'var(--warn)' },
  unlikely: { tone: 'bad', label: 'Unlikely', color: 'var(--down)' }
} as const;

function waitText(days: number | null): string {
  if (!days) return 'Never in the model';
  if (days < 2) return '1–2 days';
  if (days < 60) return `About ${Math.round(days)} days`;
  if (days < 730) return `About ${Math.round(days / 30)} months`;
  return `About ${(days / 365).toFixed(0)} years`;
}

function TargetCard({ status, refresh }: { status: Status; refresh: () => void }) {
  const current = status.target.daily_target_usd;
  const [usdIn, setUsdIn] = useState(current ? String(current) : '');
  const [funds, setFunds] = useState(status.equity.futures ? String(Math.round(status.equity.futures)) : '');
  const [closeOpen, setCloseOpen] = useState(status.target.close_open);
  const [a, setA] = useState<Assessment | null>(null);
  const [loading, setLoading] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const { busy, run } = useBotActions(refresh);
  const value = Number(usdIn);
  const valid = usdIn !== '' && value > 0 && Number(funds) > 0;

  useEffect(() => { setA(null); }, [usdIn, funds]);

  const assess = async () => {
    setLoading(true);
    try {
      const r = await api.assess(value, Number(funds));
      if (!r.ok) toast.error(r.reason || 'Couldn’t assess this target');
      setA(r);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Couldn’t assess this target');
    } finally {
      setLoading(false);
    }
  };

  const v = a?.ok ? VERDICT[a.verdict] : null;
  const progress = current ? Math.max(0, Math.min(1, status.target.realized_today / current)) : 0;
  return (
    <section className="panel" aria-labelledby="tgt-h">
      <div className="panel-head">
        <div>
          <h3 id="tgt-h">Daily profit target</h3>
          <div className="sub">Once today's realized P&amp;L (both bots) reaches it, no new trades until 00:00 UTC.</div>
        </div>
        {current ? <Chip tone={status.target.reached ? 'ok' : 'info'} icon="flag">{status.target.reached ? 'Reached' : `${usd(current)} set`}</Chip> : <Chip>Off</Chip>}
      </div>
      <div className="panel-body assess">
        {current && (
          <div className="grid" style={{ gap: 6 }}>
            <div className="t-small muted num">Today {usd(status.target.realized_today, true)} of {usd(current)}</div>
            <div className="meter"><span style={{ width: `${progress * 100}%`, background: 'var(--up)' }} /></div>
          </div>
        )}
        <div className="grid cols-2" style={{ gap: 12 }}>
          <div className="field">
            <label htmlFor="tgt">Target for the day</label>
            <div className="box"><span className="affix">$</span><input id="tgt" inputMode="decimal" type="number" min="0" step="1" value={usdIn} onChange={e => setUsdIn(e.target.value)} placeholder="e.g. 20" /></div>
          </div>
          <div className="field">
            <label htmlFor="funds">Funds in the account</label>
            <div className="box"><span className="affix">$</span><input id="funds" inputMode="decimal" type="number" min="0" step="10" value={funds} onChange={e => setFunds(e.target.value)} placeholder="Your demo balance" /></div>
            <span className="help">{status.equity.futures ? `Last seen by the futures bot: ${usd(status.equity.futures)}` : 'Start the futures bot to fill this in automatically.'}</span>
          </div>
        </div>
        <div className="switch-row" style={{ paddingTop: 0 }}>
          <div><div className="t">Also close open positions when it's reached</div><div className="d">Off: open trades keep running to their stop or exit. On: they are closed at market.</div></div>
          <Switch checked={closeOpen} onChange={setCloseOpen} label="Close open positions at the target" />
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <Btn kind="tonal" icon="analytics" disabled={!valid} busy={loading} onClick={assess}>Assess the risk</Btn>
          {!valid && <span className="why-disabled">{usdIn === '' || value <= 0 ? 'Enter a target above $0 to assess it.' : 'Enter the funds in the account.'}</span>}
          {current && <Btn kind="text" busy={busy === 'clear'} onClick={() => run('clear', () => api.setTarget(null, false))}>Turn off</Btn>}
        </div>

        {loading && !a && <Skeleton h={160} r={12} />}
        {a?.ok && v && (
          <div className="tonal fade-in" style={{ padding: 16, display: 'grid', gap: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
              <Chip tone={v.tone}>{v.label}</Chip>
              <span className="t-title-s">{a.summary}</span>
            </div>
            <div className="grid" style={{ gap: 6 }}>
              <div className="t-small muted num">Days that would have reached {usd(a.target_usd)}: {(a.p_hit_day * 100).toFixed(1)}%</div>
              <div className="meter"><span style={{ width: `${Math.max(1, a.p_hit_day * 100)}%`, background: v.color }} /></div>
            </div>
            <div className="stat-row num">
              <div><div className="k">Typical wait for a hit</div><div className="v">{waitText(a.days_to_first_hit)}</div></div>
              <div><div className="k">Average day</div><div className={`v ${a.expected_day_usd >= 0 ? 'up' : 'down'}`}>{usd(a.expected_day_usd, true)}</div></div>
              <div><div className="k">Days with no trade</div><div className="v">{Math.round(a.p_no_trade_day * 100)}%</div></div>
            </div>
            <ul className="muted" style={{ margin: 0, paddingLeft: 18, display: 'grid', gap: 4 }}>
              {a.notes.map(n => <li key={n}>{n}</li>)}
            </ul>
            <p className="t-small faint">{a.method}</p>
            <div><Btn kind="filled" icon="flag" onClick={() => setConfirm(true)}>Set {usd(a.target_usd)} target</Btn></div>
          </div>
        )}
      </div>
      <Dialog open={confirm} onClose={() => setConfirm(false)} icon="flag" title={`Set a ${usd(value)} daily target?`}
        actions={<>
          <Btn kind="text" onClick={() => setConfirm(false)}>Cancel</Btn>
          <Btn kind="filled" onClick={() => { setConfirm(false); run('set', () => api.setTarget(value, closeOpen)); }}>Set target</Btn>
        </>}>
        <ul>
          <li>Once both bots' realized P&amp;L today reaches {usd(value)}, they take no new trades until 00:00 UTC.</li>
          <li>{closeOpen ? 'Open positions are closed at market at that moment.' : 'Open positions keep running to their stop or exit signal.'}</li>
          <li>The target doesn't make the bots trade more or risk more. {a?.ok ? `The estimate says it's ${VERDICT[a.verdict].label.toLowerCase()}.` : ''}</li>
        </ul>
      </Dialog>
    </section>
  );
}

function KillCard({ status, refresh }: { status: Status; refresh: () => void }) {
  const { busy, run } = useBotActions(refresh);
  const [resume, setResume] = useState(false);
  const on = status.kill_switch;
  const running = (['spot', 'futures'] as const).filter(b => status.bots[b].running);
  return (
    <section className="panel" aria-labelledby="kill-h">
      <div className="panel-head"><div><h3 id="kill-h">Safety</h3><div className="sub">Limits that hold no matter what a strategy says</div></div></div>
      <div className="panel-body">
        <div className="switch-row">
          <div>
            <div className="t">Pause new entries</div>
            <div className="d">Creates the KILL file. Both bots stop opening trades; stops and exits keep working.</div>
          </div>
          <Switch danger checked={on} disabled={busy === 'kill'} label="Pause new entries"
            onChange={v => (v ? run('kill', () => api.setKill(true)) : setResume(true))} />
        </div>
        <hr className="divider" />
        <div className="facts three num" style={{ margin: '0 -20px -20px' }}>
          <div className="fact"><div className="k">Spot daily loss limit</div><div className="v">{usd(status.limits.spot_daily_loss)}</div></div>
          <div className="fact"><div className="k">Futures daily loss limit</div><div className="v">{usd(status.limits.futures_daily_loss)}</div></div>
          <div className="fact"><div className="k">Spot position cap</div><div className="v">{usd(status.limits.spot_max_notional)}</div></div>
          <div className="fact"><div className="k">Futures risk per trade</div><div className="v">{(status.limits.futures_risk * 100).toFixed(0)}% of equity</div></div>
          <div className="fact"><div className="k">Futures margin cap</div><div className="v">{Math.round(status.limits.futures_max_margin * 100)}% of equity</div></div>
          <div className="fact"><div className="k">Max leverage</div><div className="v">{status.limits.futures_max_leverage}×, isolated</div></div>
        </div>
      </div>
      <Dialog open={resume} onClose={() => setResume(false)} icon="play_circle" title="Allow new entries again?"
        actions={<>
          <Btn kind="text" onClick={() => setResume(false)}>Keep paused</Btn>
          <Btn kind="filled" onClick={() => { setResume(false); run('kill', () => api.setKill(false)); }}>Allow entries</Btn>
        </>}>
        <p>{running.length
          ? `The ${running.join(' and ')} bot${running.length > 1 ? 's' : ''} will open trades again on the next signal.`
          : 'No bot is running, so nothing trades until you start one.'}</p>
      </Dialog>
    </section>
  );
}

export function Controls({ data, now }: { data: ConsoleData; now: number }) {
  const s = data.status;
  if (!s) return <Skeleton h={500} r={16} />;
  const logs = (['spot', 'futures'] as const).filter(b => s.bots[b].launch_log.length);
  return (
    <div className="overview-grid">
      <div className="grid" style={{ gap: 16 }}>
        <BotPanel status={s} refresh={data.refresh} now={now} />
        <TargetCard status={s} refresh={data.refresh} />
      </div>
      <div className="grid" style={{ gap: 16 }}>
        <KillCard status={s} refresh={data.refresh} />
        <section className="panel" aria-labelledby="health-h">
          <div className="panel-head">
            <div><h3 id="health-h">Latest health check</h3><div className="sub">{s.health.title}</div></div>
            {s.health.status && <Chip tone={s.health.status === 'OK' ? 'ok' : 'bad'}>{s.health.status === 'OK' ? 'OK' : 'Attention'}</Chip>}
          </div>
          <div className="panel-body">
            <ul className="muted" style={{ margin: 0, paddingLeft: 18, display: 'grid', gap: 6 }}>
              {s.health.lines.map(l => <li key={l}>{l}</li>)}
            </ul>
            <p className="t-small faint" style={{ marginTop: 12 }}>
              {s.errors_24h} warnings or errors in the last 24 h{s.last_error ? `. Latest: ${s.last_error}` : '.'}
            </p>
          </div>
        </section>
        {logs.length > 0 && (
          <section className="panel" aria-labelledby="launch-h">
            <div className="panel-head"><div><h3 id="launch-h">Launch output</h3><div className="sub">Last lines from bots started here</div></div></div>
            <div className="panel-body grid" style={{ gap: 12 }}>
              {logs.map(b => (
                <div key={b}><div className="t-label muted" style={{ marginBottom: 4 }}>{b}</div>
                  <pre className="tonal num" style={{ margin: 0, padding: 12, fontSize: 12, lineHeight: '16px', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>{s.bots[b].launch_log.join('\n')}</pre>
                </div>
              ))}
            </div>
          </section>
        )}
        <section className="panel" aria-labelledby="phone-h">
          <div className="panel-head"><div><h3 id="phone-h">Open it on your phone</h3></div><Icon name="smartphone" className="faint" /></div>
          <div className="panel-body grid" style={{ gap: 8 }}>
            <p className="muted">Start the console with <code>python dashboard.py --lan</code> (or <code>start_dashboard_lan.bat</code>). Its window prints a private link with a token; open it on a phone on the same Wi-Fi.</p>
            <p className="t-small faint">Anyone with that link can start and stop the bots, so don't share it. Updated {time(s.now)}.</p>
          </div>
        </section>
      </div>
    </div>
  );
}
