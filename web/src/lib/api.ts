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

// --- SiGen -----------------------------------------------------------------------
export type SigenMarket = 'spot' | 'futures';
export type SignalState = 'entry' | 'exit' | 'holding' | 'armed' | 'held' | 'watching';

export interface RegimeRule { measure: string; side: 'below' | 'above'; threshold: number; why?: string }
export interface SignalRegime {
  er_30: number | null; er_60: number | null; chop_14: number | null; adx_14: number | null;
  trend_strategy: boolean; choppy: boolean; mode: 'on' | 'shadow' | 'none'; rule: RegimeRule | null;
  held_back: boolean; would_hold: boolean;
}
export interface RegimeStats { trades: number; avg_r: number | null; total_r: number; win_rate_pct: number | null; profit_factor: number | null; max_dd_r: number }
export interface RegimeEvidence {
  enabled: boolean; reason: string; rule: (RegimeRule & { gain_r?: number; kept_pct?: number }) | null; shadow: RegimeRule | null;
  trades: number; trend_trades: number; from: string; to: string; calibrate_until: string; generated_at: string;
  checks?: Record<string, boolean>;
  validation?: { all: RegimeStats; kept: RegimeStats; held_back: RegimeStats; gain_r: number; luck_beaten_pct: number };
  replay?: { signals: number; all: RegimeStats; kept: RegimeStats; held_back: RegimeStats };
}

export interface SigenTerms {
  version: string;
  title: string;
  sections: [string, string][];
  statements: [string, string][];
}

export interface SigenStatus {
  terms: { accepted: boolean; version: string; accepted_at: string | null; name: string | null };
  terms_text: SigenTerms;
  scan: { state: 'never' | 'running' | 'done' | 'error'; step?: string; done?: number; total?: number; coin?: string;
    started_at?: string; finished_at?: string; error?: string };
  generated_at: string | null;
  coins: string[];
  regime: RegimeEvidence | null;
}

export interface Signal {
  id: string;
  coin: string;
  symbol: string;
  market: SigenMarket;
  timeframe: string;
  strategy: string;
  label: string;
  rule: string;
  state: SignalState;
  direction: 'long' | 'short' | null;
  action: string;
  instruction: string;
  price: number;
  bar_time: string;
  next_decision: string;
  signal_time: string | null;
  entry: number | null;
  stop: number | null;
  initial_stop?: number;
  target: number | null;
  trail: string | null;
  exit_rule: string | null;
  exit_price?: number;
  exit_reason?: string;
  result_r?: number;
  r_now?: number;
  headline: string;
  checks: Check[];
  checks_at: 'now' | 'entry';
  regime?: SignalRegime;
  valid_from: string;
  valid_until: string;
  chase_limit?: number;
  late_entry_ok?: boolean;
  entry_bar: string | null;
  trigger: Partial<Record<'long' | 'short', string>>;
  confidence: { score: number; label: 'High' | 'Medium' | 'Low';
    parts: { edge_certainty: number; folds_positive: number; ai_setup: number; ai_weight: number; unusual_market: boolean } };
  accuracy: { win_rate_pct: number; expected_win_rate_pct: number; trades: number; profit_factor: number; avg_win_r: number;
    avg_loss_r: number; folds_positive: number; return_pct: number; max_drawdown_pct: number; history_days?: number };
  ai: { p_win: number | null; di: number | null; unusual: boolean; base_rate: number; holdout_auc: number;
    drivers?: { feature: string; effect: 'for' | 'against'; weight: number }[] };
}

export interface SigenSignals {
  market: SigenMarket;
  scanned: boolean;
  generated_at?: string;
  coins?: string[];
  universe_source?: string;
  signals: Signal[];
  untested: { coin: string; reason: string; closest: { strategy: string; profit_factor: number; trades: number; folds_positive: number } | null }[];
  errors?: { coin: string; error: string }[];
  model?: {
    trained_on: number; coins: number; base_rate: number; di_threshold: number; trained_at: string;
    importance: Record<string, number>;
    holdout: { trades: number; auc: number; auc_pooled: number; brier_skill: number; from: string; to: string;
      calibration: { predicted: number; actual: number; trades: number }[] };
  };
}

export interface JournalOutcome {
  status: 'won' | 'lost' | 'flat' | 'open' | 'no data';
  verdict: string;
  exit_price?: number;
  exit_reason?: string;
  exit_time?: string;
  result_r?: number;
  r_now?: number;
  price?: number;
  stop_now?: number;
  move_pct?: number;
  bars_held?: number;
  mfe_r?: number;
  mae_r?: number;
  trail_moved?: boolean;
  as_of?: string;
  note?: string;
  entry_window: { next_open: number; enterable: boolean } | null;
}

export interface JournalRow {
  id: string;
  source: 'live' | 'replay';
  late: boolean;
  market: SigenMarket;
  coin: string;
  symbol: string;
  direction: 'long' | 'short';
  strategy: string;
  label: string;
  rule: string;
  timeframe: string;
  entry_bar: string;
  signal_time: string;
  valid_from: string;
  valid_until: string;
  entry: number;
  stop: number;
  target: number | null;
  chase_limit: number | null;
  trail: string | null;
  exit_rule: string | null;
  instruction: string;
  confidence: { score: number; label: string };
  regime?: SignalRegime;
  tested: { win_rate_pct: number; expected_win_rate_pct: number; trades: number; profit_factor: number };
  recorded_at: string;
  outcome: JournalOutcome;
}

export interface JournalSummary {
  signals: number; closed: number; open: number; won: number; lost: number; flat: number;
  win_rate_pct: number | null; tested_win_rate_pct: number | null; avg_r: number | null; total_r: number;
  trial: { would_hold: TrialSide; kept: TrialSide; enough: boolean; needed: number };
}
export interface TrialSide { closed: number; avg_r: number | null; total_r: number; won: number }

export interface JournalReport {
  generated_at: string;
  summary: Record<'live' | 'replay', JournalSummary>;
  signals: JournalRow[];
  flat_r: number;
  chase_r: number;
}

export const sigenApi = {
  status: () => get<SigenStatus>('/api/sigen'),
  signals: (market: SigenMarket) => get<SigenSignals>(`/api/sigen/signals?market=${market}`),
  chart: (market: SigenMarket, coin: string) => get<Analysis>(`/api/sigen/chart?market=${market}&coin=${encodeURIComponent(coin)}`),
  accept: (name: string, statements: string[], version: string) => post('/api/sigen/accept', { name, statements, version }),
  scan: () => post('/api/sigen/scan'),
  journal: () => get<JournalReport>('/api/sigen/journal'),
  backfill: (days = 30) => post('/api/sigen/backfill', { days }),
  journalCsv: '/api/sigen/journal.csv'
};
