import type { Analysis, Check, SideView } from '../lib/api';
import { price } from '../lib/format';
import { Icon } from './ui';

/** The price a side needs a close beyond (from the server); null when it waits on an indicator. */
export function triggerLevel(side: SideView | undefined): number | null {
  return side?.trigger_level ?? null;
}

export function Checklist({ checks }: { checks: Check[] }) {
  return (
    <div className="checks">
      {checks.map(c => (
        <div key={c.label} className={`check${c.ok ? ' ok' : ''}`}>
          <span className="tick"><Icon name={c.ok ? 'check' : 'remove'} /></span>
          <div>
            <div className="lbl">{c.label}</div>
            <div className="det num">{c.detail}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function MoodTag({ mood }: { mood?: Analysis['mood'] }) {
  if (!mood) return null;
  const m = { waiting: ['hourglass_top', 'Watching'], signal: ['bolt', 'Signal'], holding: ['trending_up', 'In a trade'] }[mood];
  return <span className={`mood ${mood}`}><Icon name={m[0]} fill />{m[1]}</span>;
}

/**
 * A price rail centred on the last close: a tick for "now" and a dashed tick for each
 * side's trigger, on a real % scale (the same levels the chart draws as dashed lines).
 */
export function TriggerGauge({ close, sides }: { close: number; sides: Analysis['sides'] }) {
  const d = (lv: number) => (lv / close - 1) * 100;
  const fmt = (v: number) => `${v > 0 ? '+' : '−'}${Math.abs(v).toFixed(1)}%`;
  const marks = (['long', 'short'] as const)
    .filter(k => sides[k])
    .map(k => ({ side: k, level: triggerLevel(sides[k]) }));
  const dists = marks.filter(m => m.level !== null).map(m => Math.abs(d(m.level as number)));
  const w = Math.max(8, 1.2 * Math.max(0, ...dists));
  const x = (pct: number) => 50 + (pct / w) * 50;
  const label = marks.map(m => (m.level === null ? `${m.side} waits on an indicator` : `${m.side} trigger ${fmt(d(m.level))} at ${price(m.level)}`)).join('; ');
  return (
    <div className="rail-gauge" role="img" aria-label={label}>
      <div className="track">
        {marks.map(m => m.level !== null && (
          <span key={m.side} className={`gap ${m.side}`}
            style={{ left: `${Math.min(50, x(d(m.level)))}%`, width: `${Math.abs(x(d(m.level)) - 50)}%` }} />
        ))}
        {marks.map(m => m.level !== null && (
          <span key={m.side + 't'} className={`tick ${m.side}`} style={{ left: `${x(d(m.level))}%` }} />
        ))}
        <span className="now" style={{ left: '50%' }} />
      </div>
      <div className="legend num">
        {marks.map(m => (
          <span key={m.side} className={m.side}>
            {m.side === 'long' ? 'Long' : 'Short'} {m.level === null ? <i title="Waits on an indicator, not a price">no price trigger</i> : <b>{fmt(d(m.level))}</b>}
          </span>
        ))}
      </div>
    </div>
  );
}
