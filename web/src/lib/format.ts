export const coin = (symbol: string) => symbol.split('/')[0];
export const market = (symbol: string) => (symbol.includes(':') ? 'Perpetual' : 'Spot');

export function price(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v)) return '—';
  const a = Math.abs(v);
  const digits = a >= 1000 ? 2 : a >= 100 ? 2 : a >= 1 ? 4 : 5;
  return v.toLocaleString('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

export function usd(v: number | null | undefined, signed = false): string {
  if (v === null || v === undefined || Number.isNaN(v)) return '—';
  const s = Math.abs(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  if (!signed) return `${v < 0 ? '−' : ''}$${s}`;
  return `${v > 0 ? '+' : v < 0 ? '−' : ''}$${s}`;
}

export const pct = (v: number, digits = 1) => `${v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v).toFixed(digits)}%`;
export const r = (v: number | null | undefined) => (v === null || v === undefined ? '—' : `${v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v).toFixed(2)}R`);
export const tone = (v: number | null | undefined) => (!v ? '' : v > 0 ? 'up' : 'down');

export function time(iso: string | null | undefined, withDate = true): string {
  if (!iso) return '—';
  const d = new Date(iso);
  const t = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  if (!withDate) return t;
  const today = new Date();
  const y = new Date(today); y.setDate(today.getDate() - 1);
  if (d.toDateString() === today.toDateString()) return `Today ${t}`;
  if (d.toDateString() === y.toDateString()) return `Yesterday ${t}`;
  return `${d.toLocaleDateString([], { month: 'short', day: 'numeric' })} ${t}`;
}

export function dayLabel(iso: string): string {
  const d = new Date(iso);
  const today = new Date();
  const y = new Date(today); y.setDate(today.getDate() - 1);
  if (d.toDateString() === today.toDateString()) return 'Today';
  if (d.toDateString() === y.toDateString()) return 'Yesterday';
  return d.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' });
}

export function ago(iso: string | null | undefined, now = Date.now()): string {
  if (!iso) return '—';
  const s = Math.max(0, Math.round((now - new Date(iso).getTime()) / 1000));
  if (s < 45) return 'just now';
  const m = Math.round(s / 60);
  if (m < 60) return `${m} min ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h} h ${m % 60} min ago`;
  return `${Math.floor(h / 24)} d ${h % 24} h ago`;
}

export function until(iso: string | null | undefined, now = Date.now()): string {
  if (!iso) return '—';
  const s = Math.round((new Date(iso).getTime() - now) / 1000);
  if (s <= 0) return 'any moment';
  const m = Math.floor(s / 60);
  if (m < 1) return `in ${s} s`;
  if (m < 60) return `in ${m} min`;
  return `in ${Math.floor(m / 60)} h ${m % 60} min`;
}

export function duration(a: string | null, b: string | null): string {
  if (!a || !b) return '—';
  const m = Math.round((new Date(b).getTime() - new Date(a).getTime()) / 60000);
  if (m < 60) return `${m} min`;
  const h = Math.floor(m / 60);
  if (h < 48) return `${h} h ${m % 60} min`;
  return `${Math.floor(h / 24)} d ${h % 24} h`;
}

const REASONS: Record<string, string> = {
  stop: 'Stop-loss',
  signal: 'Exit signal',
  tp: 'Take-profit',
  'trailing stop': 'Trailing stop',
  'exchange stop/tp': 'Stop on OKX',
  manual: 'Closed by you',
  'daily target': 'Daily target',
  'stop placement failed': 'Safety close',
  'liquidation price inside stop': 'Safety close'
};
export const reasonLabel = (r: string) => REASONS[r] || (r ? r[0].toUpperCase() + r.slice(1) : '—');

/** "supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts" -> "Supertrend" */
export function strategyName(label: string): string {
  const n = label.split('(')[0];
  const names: Record<string, string> = {
    supertrend: 'Supertrend', donchian_breakout: 'Donchian breakout', breakout_htf: 'HTF breakout',
    trend_pullback: 'Trend pullback', pullback_htf: 'HTF pullback', bollinger_reversion: 'Bollinger reversion',
    ema_cross: 'EMA cross', ema_cross_adx: 'EMA cross + ADX', chandelier_trend: 'Chandelier trend'
  };
  return names[n] || n;
}
