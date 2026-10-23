import { useEffect, useState } from 'react';
import { Toaster } from 'sonner';
import { useConsoleData, useNow, useRoute, hrefFor, type Route } from './lib/store';
import { ago } from './lib/format';
import { Btn, Chip, Icon } from './components/ui';
import { Overview } from './pages/Overview';
import { Strategies } from './pages/Strategies';
import { Trades } from './pages/Trades';
import { Activity } from './pages/Activity';
import { Controls } from './pages/Controls';

const NAV: { page: Route['page']; label: string; icon: string }[] = [
  { page: 'overview', label: 'Overview', icon: 'space_dashboard' },
  { page: 'strategies', label: 'Strategies', icon: 'insights' },
  { page: 'trades', label: 'Trades', icon: 'receipt_long' },
  { page: 'activity', label: 'Activity', icon: 'history' },
  { page: 'controls', label: 'Controls', icon: 'tune' }
];

const HEADS: Record<Route['page'], [string, string]> = {
  overview: ['Overview', 'Profit and loss, open positions, and what every strategy is looking for right now.'],
  strategies: ['Strategies', 'Each strategy on its latest closed candle: the conditions it checks, which hold, and the price that would trigger it.'],
  trades: ['Trades', 'Every closed trade. Open one to see the candles, why it entered, and how it ended.'],
  activity: ['Activity', 'Every order, skipped signal, stop move, start, stop and error, newest first.'],
  controls: ['Controls', 'Start and stop the bots, pause new entries, and set a daily profit target.']
};

type Theme = 'system' | 'light' | 'dark';

function useTheme(): [Theme, () => void] {
  const [theme, setTheme] = useState<Theme>(() => {
    try { return (localStorage.getItem('tp-theme') as Theme) || 'system'; } catch { return 'system'; }
  });
  useEffect(() => {
    if (theme === 'system') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem('tp-theme', theme); } catch { /* private mode */ }
  }, [theme]);
  return [theme, () => setTheme(t => (t === 'system' ? 'dark' : t === 'dark' ? 'light' : 'system'))];
}

function NavItem({ item, current, badge }: { item: (typeof NAV)[number]; current: boolean; badge?: boolean }) {
  return (
    <a className="rail-item" href={hrefFor({ page: item.page } as Route)} aria-current={current ? 'page' : undefined}>
      <span className="pill"><Icon name={item.icon} />{badge && <span className="badge" aria-label="needs attention" />}</span>
      <span className="lbl">{item.label}</span>
    </a>
  );
}

export default function App() {
  const data = useConsoleData();
  const [route, go] = useRoute();
  const [theme, cycleTheme] = useTheme();
  const now = useNow(10_000);
  const [scrolled, setScrolled] = useState(false);
  const s = data.status;

  useEffect(() => {
    const on = () => setScrolled(window.scrollY > 4);
    window.addEventListener('scroll', on, { passive: true });
    return () => window.removeEventListener('scroll', on);
  }, []);
  useEffect(() => { window.scrollTo({ top: 0 }); }, [route.page]);
  useEffect(() => {
    const title = HEADS[route.page][0];
    document.title = s ? `${title} · Tradepilot` : 'Tradepilot Console';
  }, [route.page, s]);

  const running = s ? (['spot', 'futures'] as const).filter(b => s.bots[b].running).length : 0;
  const attention = !!s && (s.health.status === 'ATTENTION' || s.positions.some(p => !s.bots[p.bot].running));
  const [title, sub] = HEADS[route.page];

  return (
    <div className="shell">
      <nav className="rail" aria-label="Main">
        <div className="rail-logo" aria-hidden><Icon name="moving" /></div>
        {NAV.map(n => <NavItem key={n.page} item={n} current={route.page === n.page} badge={n.page === 'controls' && attention} />)}
        <div className="rail-spacer" />
        <button className="rail-item" onClick={cycleTheme} title={`Theme: ${theme}`}>
          <span className="pill"><Icon name={theme === 'dark' ? 'dark_mode' : theme === 'light' ? 'light_mode' : 'contrast'} /></span>
          <span className="lbl">{theme === 'system' ? 'Auto' : theme === 'dark' ? 'Dark' : 'Light'}</span>
        </button>
      </nav>

      <div className="main">
        <header className={`topbar${scrolled ? ' scrolled' : ''}`}>
          <div className="brand">
            <span className="mobile-logo" aria-hidden><Icon name="moving" /></span>
            <h1>Tradepilot</h1>
            <Chip tone="demo" icon="science" title="Simulated trading on OKX demo: no real money">Demo</Chip>
          </div>
          <span className="grow" />
          {s && (
            <span className="hide-sm" style={{ display: 'inline-flex', gap: 8 }}>
              <Chip tone={running === 2 ? 'ok' : running ? 'warn' : ''} icon={running ? 'radio_button_checked' : 'radio_button_unchecked'}>
                {running === 2 ? 'Both bots running' : running ? '1 of 2 bots running' : 'Bots stopped'}
              </Chip>
              {s.kill_switch && <Chip tone="warn" icon="block">Entries paused</Chip>}
              {s.target.daily_target_usd && <Chip tone={s.target.reached ? 'ok' : 'info'} icon="flag">{s.target.reached ? 'Target reached' : `Target $${s.target.daily_target_usd}`}</Chip>}
            </span>
          )}
          <span className="updated hide-sm" aria-live="polite">{data.error ? <span className="down">Can't reach the console server</span> : data.updated ? `Updated ${ago(new Date(data.updated).toISOString(), now)}` : 'Loading…'}</span>
          <Btn kind="tonal" icon="refresh" busy={data.loading} onClick={data.refresh} title="Update everything now"><span className="btn-label">Update</span></Btn>
        </header>

        <main className="page" id="main">
          {data.error && !s && (
            <div className="banner bad" style={{ marginBottom: 16 }}>
              <Icon name="cloud_off" />
              <div className="grow"><b>The console server isn't answering.</b> Is <code>dashboard.py</code> still running? ({data.error})</div>
              <div className="actions"><Btn kind="text" small onClick={data.refresh}>Retry</Btn></div>
            </div>
          )}
          <div className="page-head">
            <div><h2>{title}</h2><p>{sub}</p></div>
          </div>
          {route.page === 'overview' && <Overview data={data} go={go} now={now} />}
          {route.page === 'strategies' && <Strategies data={data} route={route} go={go} now={now} />}
          {route.page === 'trades' && <Trades data={data} route={route} go={go} />}
          {route.page === 'activity' && <Activity data={data} />}
          {route.page === 'controls' && <Controls data={data} now={now} />}
        </main>
      </div>

      <nav className="bottom-nav" aria-label="Main">
        {NAV.map(n => <NavItem key={n.page} item={n} current={route.page === n.page} badge={n.page === 'controls' && attention} />)}
      </nav>
      <Toaster position="bottom-center" richColors closeButton theme={theme === 'system' ? 'system' : theme} offset={24} mobileOffset={{ bottom: 96 }} />
    </div>
  );
}
