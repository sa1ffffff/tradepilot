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
 * Where price sits between the short trigger (left) and the long trigger (right).
 * A one-sided strategy shows how close price is to its single trigger.
 */
export function TriggerGauge({ close, sides }: { close: number; sides: Analysis['sides'] }) {
  const lt = triggerLevel(sides.long);
  const st = triggerLevel(sides.short);
  const d = (lv: number) => (lv / close - 1) * 100;
  const fmt = (v: number) => `${v > 0 ? '+' : '−'}${Math.abs(v).toFixed(1)}%`;
  if (lt === null && st === null) {
    return <div className="rail-gauge"><div className="legend"><span>No price trigger: waits on an indicator</span></div></div>;
  }
  if (lt !== null && st !== null && lt > close && st < close) {
    const pos = ((close - st) / (lt - st)) * 100;
    return (
      <div className="rail-gauge" role="img" aria-label={`Long trigger ${fmt(d(lt))} away, short trigger ${fmt(d(st))} away`}>
        <div className="track">
          <span className="fill short" style={{ left: 0, width: `${Math.max(2, pos)}%`, opacity: 0.28 }} />
          <span className="fill long" style={{ left: `${pos}%`, width: `${Math.max(2, 100 - pos)}%`, opacity: 0.28 }} />
          <span className="mid" style={{ left: `${pos}%` }} />
        </div>
        <div className="legend num"><span>Short <b>{fmt(d(st))}</b></span><span>Long <b>{fmt(d(lt))}</b></span></div>
      </div>
    );
  }
  const lv = (lt ?? st) as number;
  const side = lt !== null ? 'long' : 'short';
  const away = Math.abs(d(lv));
  const near = Math.max(4, 100 - Math.min(away / 8, 1) * 100);
  return (
    <div className="rail-gauge" role="img" aria-label={`${side} trigger ${fmt(d(lv))} away at ${price(lv)}`}>
      <div className="track"><span className={`fill ${side}`} style={{ left: 0, width: `${near}%` }} /></div>
      <div className="legend num"><span>{side === 'long' ? 'Long' : 'Short'} trigger {price(lv)}</span><b>{fmt(d(lv))}</b></div>
    </div>
  );
}
