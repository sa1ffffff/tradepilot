import { useMemo, useState } from 'react';
import type { ActivityRow } from '../lib/api';
import type { ConsoleData } from '../lib/store';
import { coin, dayLabel, price, reasonLabel, time, usd } from '../lib/format';
import { Empty, FilterChip, Icon, Skeleton } from '../components/ui';

type Kind = 'fills' | 'skips' | 'stops' | 'lifecycle' | 'problems';

const KIND: Record<string, Kind> = {
  entry_filled: 'fills', exit_filled: 'fills', entry_skipped: 'skips', entry_unfilled: 'problems', entry_retry: 'problems',
  stop_trailed: 'stops', trail_hit: 'stops', stop_missing_replacing: 'problems', stop_failed_closing: 'problems',
  liq_inside_stop_closing: 'problems', foreign_position: 'problems', position_missing: 'problems',
  started: 'lifecycle', stopped: 'lifecycle', error: 'problems', network_error: 'problems'
};

const LABELS: Record<Kind, string> = { fills: 'Orders filled', skips: 'Skipped signals', stops: 'Stop moves', lifecycle: 'Starts & stops', problems: 'Problems' };

function describe(e: ActivityRow): { icon: string; tone: string; title: string; detail: string } {
  const sym = e.symbol ? coin(String(e.symbol)) : 'BTC';
  const side = e.side ? String(e.side) : 'long';
  switch (e.msg) {
    case 'entry_filled':
      return { icon: side === 'short' ? 'south_east' : 'north_east', tone: 'fill-entry', title: `${side === 'short' ? 'Sold short' : 'Bought'} ${sym} at ${price(e.price)}`,
        detail: [`size ${e.size}`, e.leverage ? `${e.leverage}×` : '', `stop ${price(e.stop)}`, e.risk_usd ? `risk ${usd(Number(e.risk_usd))}` : '',
          e.maker_share !== undefined ? `${Math.round(Number(e.maker_share) * 100)}% limit fill` : ''].filter(Boolean).join(' · ') };
    case 'exit_filled': {
      const pnl = Number(e.pnl || 0);
      return { icon: 'logout', tone: pnl > 0 ? 'fill-win' : 'fill-loss', title: `Closed ${sym} ${side} at ${price(e.price)}: ${usd(pnl, true)}`,
        detail: `${reasonLabel(String(e.reason || ''))} · entry ${price(e.entry)}` };
    }
    case 'entry_skipped':
      return { icon: 'do_not_disturb_on', tone: '', title: `Skipped a ${side} signal on ${sym}`, detail: String(e.reason || '') };
    case 'stop_trailed':
      return { icon: 'trending_flat', tone: '', title: `Trailed the ${sym} stop to ${price(e.to)}`, detail: `from ${price(e.from)} · best price ${price(Number(e.best))} · locks in ${usd(Number(e.locked_pnl), true)}` };
    case 'trail_hit':
      return { icon: 'flag', tone: '', title: `${sym} hit its trailing stop`, detail: `stop ${price(e.stop)}` };
    case 'started':
      return { icon: 'play_circle', tone: '', title: `${e.bot === 'spot' ? 'Spot' : 'Futures'} bot started`,
        detail: e.bot === 'spot' ? `${e.symbol} ${e.timeframe} · ${e.strategy}` : `${(e.strategies as string[] | undefined)?.length ?? 0} strategies · ${Math.round(Number(e.risk_per_trade) * 100)}% risk per trade` };
    case 'stopped':
      return { icon: 'stop_circle', tone: '', title: `${e.bot === 'spot' ? 'Spot' : 'Futures'} bot stopped`, detail: e.by === 'dashboard' ? 'from the console' : '' };
    case 'network_error':
      return { icon: 'wifi_off', tone: 'warn', title: `Network blip${e.symbol ? ` on ${sym}` : ''}`, detail: 'Retried on the next check. ' + String(e.error || '').slice(0, 120) };
    case 'entry_retry':
      return { icon: 'replay', tone: 'warn', title: `Retrying a ${sym} entry`, detail: 'The earlier attempt never reached OKX.' };
    default:
      return { icon: 'error', tone: 'warn', title: e.msg.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase()) + (e.symbol ? ` · ${sym}` : ''),
        detail: String(e.error || e.reason || e.note || '') };
  }
}

export function Activity({ data }: { data: ConsoleData }) {
  const [on, setOn] = useState<Set<Kind>>(new Set(['fills', 'skips', 'stops', 'lifecycle', 'problems']));
  const [bot, setBot] = useState<'all' | 'spot' | 'futures'>('all');
  const rows = data.activity;
  const counts = useMemo(() => {
    const c: Record<Kind, number> = { fills: 0, skips: 0, stops: 0, lifecycle: 0, problems: 0 };
    (rows || []).forEach(r => { const k = KIND[r.msg]; if (k) c[k] += 1; });
    return c;
  }, [rows]);
  const shown = (rows || []).filter(r => on.has(KIND[r.msg]) && (bot === 'all' || r.bot === bot));
  const toggle = (k: Kind) => setOn(s => { const n = new Set(s); if (n.has(k)) n.delete(k); else n.add(k); return n; });

  let lastDay = '';
  return (
    <section className="panel">
      <div className="toolbar">
        <div className="filter-chips">
          {(Object.keys(LABELS) as Kind[]).map(k => <FilterChip key={k} on={on.has(k)} onClick={() => toggle(k)} count={counts[k]}>{LABELS[k]}</FilterChip>)}
        </div>
        <span className="grow" />
        <div className="filter-chips">
          {(['all', 'spot', 'futures'] as const).map(b => <FilterChip key={b} on={bot === b} onClick={() => setBot(b)}>{b === 'all' ? 'Both bots' : b === 'spot' ? 'Spot' : 'Futures'}</FilterChip>)}
        </div>
      </div>
      {!rows ? <div className="panel-body"><Skeleton h={300} /></div> : shown.length === 0 ? (
        <Empty icon="history" title="Nothing to show">Turn on more event types above.</Empty>
      ) : (
        <div className="feed">
          {shown.map((e, i) => {
            const d = describe(e);
            const day = dayLabel(e.ts);
            const sep = day !== lastDay;
            lastDay = day;
            return (
              <div key={e.ts + i}>
                {sep && <div className="day-sep">{day}</div>}
                <div className="event">
                  <span className={`ev-icon ${d.tone}`}><Icon name={d.icon} /></span>
                  <div style={{ minWidth: 0 }}>
                    <div className="ev-title num">{d.title}</div>
                    {d.detail && <div className="ev-detail num">{d.detail}</div>}
                  </div>
                  <div className="ev-time num">{time(e.ts, false)}<div>{e.bot}</div></div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
