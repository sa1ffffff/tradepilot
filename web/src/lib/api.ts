// Types mirror dashboard.py's JSON. Every POST carries X-Tradepilot so another
// site open in the browser can't trigger an action (the server refuses without it).

export type BotName = 'spot' | 'futures';

export interface BotStatus {
  running: boolean;
  since: string | null;
  last_started: string | null;
  last_stopped: string | null;
  heartbeat: string | null;
  pid: number | null;
  equity: number | null;
  poll_seconds: number;
  stop_pending: boolean;
  launch_log: string[];
}

export interface Position {
  bot: BotName;
  symbol: string;
  side: 'long' | 'short';
  dir: number;
  entry: number;
  size: number;
  stop: number;
  tp: number | null;
  leverage: number;
  margin?: number;
  opened: string;
  price: number | null;
  unrealized: number | null;
  r_now: number | null;
  risk_usd: number;
  liq_price: number | null;
  entry_time: string | null;
  timeframe: string | null;
  close_pending: boolean;
}

export interface Slot {
  bot: BotName;
  symbol: string;
  timeframe: string;
  label: string;
  rule: string;
  risk_fraction: number;
  file: string;
  trail_start_r?: number;
  evidence: {
    trades: number;
    win_rate_pct: number;
    profit_factor: number;
    total_return_pct: number;
    max_drawdown_pct: number;
    folds_positive: number;
    verdict: string;
  } | null;
}

export interface Status {
  now: string;
  demo: boolean;
  bots: Record<BotName, BotStatus>;
  kill_switch: boolean;
  target: { daily_target_usd: number | null; close_open: boolean; set_at: string | null; realized_today: number; reached: boolean };
  limits: {
    spot_daily_loss: number;
    futures_daily_loss: number;
    spot_max_notional: number;
    futures_risk: number;
    futures_max_margin: number;
    futures_max_leverage: number;
  };
  pnl: {
    today: Record<BotName, number>;
    today_total: number;
    unrealized: number;
    all_time: number;
    trades: number;
    wins: number;
    gross_win: number;
    gross_loss: number;
    curve: [string, number][];
  };
  equity: Record<BotName, number | null>;
  positions: Position[];
  prices_ok: boolean;
  slots: Slot[];
  errors_24h: number;
  last_error: string | null;
  health: { title: string; status: string; lines: string[] };
}

export interface Trade {
  id: string;
  bot: BotName;
  symbol: string;
  side: 'long' | 'short';
  entry_time: string | null;
  exit_time: string;
  bar: string | null;
  entry: number;
  exit: number;
  size: number;
  stop: number | null;
  tp: number | null;
  leverage: number;
  risk_usd: number | null;
  pnl: number;
  r: number | null;
  reason: string;
  timeframe: string;
  strategy: string;
  slippage_bps: number | null;
  entry_maker_share: number | null;
  exit_maker_share: number | null;
}

export interface Check { label: string; ok: boolean; detail: string; level?: number }
export interface SideView { checks: Check[]; ready: boolean; trigger: string; exit: string; met: number; total: number; trigger_level: number | null }
export type Candle = [number, number, number, number, number, number];

export interface Analysis {
  bot: BotName;
  symbol: string;
  timeframe: string;
  label: string;
  rule: string;
  bar_time: string;
  bar_close_time: string;
  next_decision: string;
  close: number;
  atr: number;
  headline: string;
  mood: 'waiting' | 'signal' | 'holding';
  sides: Partial<Record<'long' | 'short', SideView>>;
  candles: Candle[];
  after?: Candle[];
  lines: { name: string; role: string; points: [number, number][] }[];
  panes: { name: string; levels: number[]; points: [number, number][] }[];
  signals: { time: number; kind: 'long_entry' | 'short_entry' }[];
  fills: { time: string; kind: 'entry' | 'exit'; side: string; price: number; reason?: string }[];
  position?: Record<string, number | string> | null;
  trade?: Trade;
}

export interface OverviewRow {
  bot: BotName;
  symbol: string;
  timeframe: string;
  label: string;
  headline?: string;
  mood?: Analysis['mood'];
  sides?: Analysis['sides'];
  close?: number;
  bar_time?: string;
  next_decision?: string;
  error?: string;
}

export interface ActivityRow {
  ts: string;
  bot: BotName;
  msg: string;
  level: string;
  symbol?: string;
  side?: string;
  reason?: string;
  price?: number;
  pnl?: number;
  entry?: number;
  stop?: number;
  from?: number;
  to?: number;
  error?: string;
  [k: string]: unknown;
}

export interface Assessment {
  ok: boolean;
  reason?: string;
  target_usd: number;
  funds: number;
  target_pct: number;
  p_hit_day: number;
  p_loss_limit_day: number;
  p_no_trade_day: number;
  expected_day_usd: number;
  trades_per_day: number;
  risk_per_trade_usd: number;
  avg_win_usd: number;
  days_to_first_hit: number | null;
  verdict: 'realistic' | 'stretch' | 'unlikely';
  summary: string;
  notes: string[];
  method: string;
}

export interface ActionResult { ok: boolean; message: string; pending?: boolean; error?: string }

async function get<T>(path: string): Promise<T> {
  const r = await fetch(path, { cache: 'no-store' });
  const body = await r.json().catch(() => ({ error: `HTTP ${r.status}` }));
  if (!r.ok) throw new Error(body.error || `HTTP ${r.status}`);
  return body as T;
}

async function post(path: string, data: unknown = {}): Promise<ActionResult> {
  const r = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Tradepilot': '1' },
    body: JSON.stringify(data)
  });
  const body = await r.json().catch(() => ({ ok: false, message: `HTTP ${r.status}` }));
  if (!r.ok) return { ok: false, message: body.error || `HTTP ${r.status}` };
  return body as ActionResult;
}

export const api = {
  status: () => get<Status>('/api/status'),
  trades: () => get<Trade[]>('/api/trades'),
  activity: () => get<ActivityRow[]>('/api/activity'),
  overview: () => get<OverviewRow[]>('/api/overview'),
  analysis: (bot: BotName, symbol: string, trade?: string) =>
    get<Analysis>(`/api/analysis?bot=${bot}&symbol=${encodeURIComponent(symbol)}${trade ? `&trade=${encodeURIComponent(trade)}` : ''}`),
  assess: (usd: number, funds?: number) =>
    get<Assessment>(`/api/target/assess?usd=${usd}${funds ? `&funds=${funds}` : ''}`),
  startBot: (bot: BotName) => post(`/api/bots/${bot}/start`),
  stopBot: (bot: BotName) => post(`/api/bots/${bot}/stop`),
  forceStopBot: (bot: BotName) => post(`/api/bots/${bot}/force-stop`),
  setKill: (on: boolean) => post('/api/kill', { on }),
  closePosition: (bot: BotName, symbol: string) => post('/api/positions/close', { bot, symbol }),
  setTarget: (usd: number | null, close_open: boolean) => post('/api/target', { daily_target_usd: usd, close_open })
};
