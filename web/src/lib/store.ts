import { useCallback, useEffect, useRef, useState } from 'react';
import { api, type ActivityRow, type OverviewRow, type Status, type Trade } from './api';

/** Polls the console API while the tab is visible; refresh() reloads everything now. */
export function useConsoleData() {
  const [status, setStatus] = useState<Status | null>(null);
  const [trades, setTrades] = useState<Trade[] | null>(null);
  const [activity, setActivity] = useState<ActivityRow[] | null>(null);
  const [overview, setOverview] = useState<OverviewRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [updated, setUpdated] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const busy = useRef(false);

  const loadStatus = useCallback(async () => {
    try {
      const s = await api.status();
      setStatus(s);
      setError(null);
      setUpdated(Date.now());
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  const loadLists = useCallback(async () => {
    const [t, a] = await Promise.allSettled([api.trades(), api.activity()]);
    if (t.status === 'fulfilled') setTrades(t.value);
    if (a.status === 'fulfilled') setActivity(a.value);
  }, []);

  const loadOverview = useCallback(async () => {
    try { setOverview(await api.overview()); } catch { /* the overview shows its own retry */ }
  }, []);

  const refresh = useCallback(async () => {
    if (busy.current) return;
    busy.current = true;
    setLoading(true);
    await Promise.allSettled([loadStatus(), loadLists(), loadOverview()]);
    busy.current = false;
    setLoading(false);
  }, [loadStatus, loadLists, loadOverview]);

  useEffect(() => {
    refresh();
    const timers = [
      window.setInterval(() => document.visibilityState === 'visible' && loadStatus(), 10_000),
      window.setInterval(() => document.visibilityState === 'visible' && loadLists(), 30_000),
      window.setInterval(() => document.visibilityState === 'visible' && loadOverview(), 60_000)
    ];
    const onVisible = () => document.visibilityState === 'visible' && loadStatus();
    document.addEventListener('visibilitychange', onVisible);
    return () => {
      timers.forEach(clearInterval);
      document.removeEventListener('visibilitychange', onVisible);
    };
  }, [refresh, loadStatus, loadLists, loadOverview]);

  return { status, trades, activity, overview, error, updated, loading, refresh, loadStatus, loadOverview };
}

export type ConsoleData = ReturnType<typeof useConsoleData>;

/** Re-render every `ms` so relative times ("2 min ago") stay current. */
export function useNow(ms = 15_000) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const t = window.setInterval(() => setNow(Date.now()), ms);
    return () => clearInterval(t);
  }, [ms]);
  return now;
}

export type Route =
  | { page: 'overview' }
  | { page: 'strategies'; bot?: string; symbol?: string }
  | { page: 'trades'; trade?: string }
  | { page: 'activity' }
  | { page: 'controls' };

export function parseHash(h: string): Route {
  const [page, a, b] = h.replace(/^#\/?/, '').split('/').map(decodeURIComponent);
  if (page === 'strategies') return { page, bot: a, symbol: b };
  if (page === 'trades') return { page, trade: a };
  if (page === 'activity' || page === 'controls') return { page };
  return { page: 'overview' };
}

export function hrefFor(r: Route): string {
  if (r.page === 'strategies' && r.bot && r.symbol) return `#/strategies/${r.bot}/${encodeURIComponent(r.symbol)}`;
  if (r.page === 'trades' && r.trade) return `#/trades/${encodeURIComponent(r.trade)}`;
  return `#/${r.page}`;
}

export function useRoute(): [Route, (r: Route) => void] {
  const [route, setRoute] = useState<Route>(() => parseHash(location.hash));
  useEffect(() => {
    const on = () => setRoute(parseHash(location.hash));
    window.addEventListener('hashchange', on);
    return () => window.removeEventListener('hashchange', on);
  }, []);
  return [route, (r: Route) => { location.hash = hrefFor(r); }];
}
