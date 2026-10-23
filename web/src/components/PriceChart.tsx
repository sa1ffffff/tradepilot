import { useEffect, useRef, useState } from 'react';
import {
  CandlestickSeries, ColorType, CrosshairMode, HistogramSeries, LineSeries, LineStyle, createChart, createSeriesMarkers,
  type IChartApi, type SeriesMarker, type Time, type UTCTimestamp
} from 'lightweight-charts';
import type { Analysis } from '../lib/api';
import { price } from '../lib/format';

const TF_SEC: Record<string, number> = { '1m': 60, '5m': 300, '15m': 900, '30m': 1800, '1h': 3600, '2h': 7200, '4h': 14400, '1d': 86400 };

/** lightweight-charts draws UTC; shift into the viewer's local time so the axis matches the rest of the page. */
const local = (sec: number) => (sec - new Date(sec * 1000).getTimezoneOffset() * 60) as UTCTimestamp;

function palette() {
  const s = getComputedStyle(document.documentElement);
  const v = (n: string) => s.getPropertyValue(n).trim();
  return {
    bg: v('--surface'), ink: v('--ink-2'), faint: v('--ink-3'), line: v('--line'), up: v('--candle-up'), down: v('--candle-down'),
    s1: v('--series-1'), s2: v('--series-2'), s3: v('--series-3'), s4: v('--series-4'), primary: v('--primary'),
    upInk: v('--up'), downInk: v('--down'), font: v('--font')
  };
}

function useThemeKey() {
  const [k, setK] = useState(0);
  useEffect(() => {
    const mq = matchMedia('(prefers-color-scheme: dark)');
    const bump = () => setK(x => x + 1);
    mq.addEventListener('change', bump);
    const mo = new MutationObserver(bump);
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    return () => { mq.removeEventListener('change', bump); mo.disconnect(); };
  }, []);
  return k;
}

export interface Level { price: number; label: string; tone: 'up' | 'down' | 'primary' | 'faint'; dashed?: boolean }

export function PriceChart({ a, levels = [], height = 420, focus }: { a: Analysis; levels?: Level[]; height?: number; focus?: { from: number; to: number } }) {
  const el = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const themeKey = useThemeKey();
  const [hover, setHover] = useState<{ o: number; h: number; l: number; c: number } | null>(null);

  useEffect(() => {
    if (!el.current) return;
    const p = palette();
    const chart = createChart(el.current, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: p.bg }, textColor: p.ink, fontFamily: p.font, fontSize: 11,
        attributionLogo: false, panes: { separatorColor: p.line, separatorHoverColor: p.line, enableResize: false }
      },
      grid: { vertLines: { color: 'transparent' }, horzLines: { color: p.line } },
      rightPriceScale: { borderVisible: false, scaleMargins: { top: 0.12, bottom: 0.08 } },
      timeScale: { borderVisible: false, timeVisible: true, secondsVisible: false, rightOffset: 4, barSpacing: 7 },
      crosshair: { mode: CrosshairMode.Normal, vertLine: { color: p.faint, labelBackgroundColor: p.ink }, horzLine: { color: p.faint, labelBackgroundColor: p.ink } },
      localization: { priceFormatter: (v: number) => price(v) },
      // the wheel scrolls the page; drag pans and dragging an axis zooms
      handleScroll: { mouseWheel: false, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: false },
      handleScale: { mouseWheel: false, pinch: true, axisPressedMouseMove: true }
    });
    chartRef.current = chart;

    const candles = chart.addSeries(CandlestickSeries, {
      upColor: p.up, downColor: p.down, wickUpColor: p.up, wickDownColor: p.down, borderVisible: false,
      priceLineVisible: false, lastValueVisible: true
    });
    const data = a.candles.map(c => ({ time: local(c[0]), open: c[1], high: c[2], low: c[3], close: c[4] }));
    candles.setData(data);

    const vol = chart.addSeries(HistogramSeries, { priceScaleId: 'vol', priceFormat: { type: 'volume' }, lastValueVisible: false, priceLineVisible: false });
    chart.priceScale('vol').applyOptions({ scaleMargins: { top: 0.86, bottom: 0 } });
    vol.setData(a.candles.map(c => ({ time: local(c[0]), value: c[5], color: (c[4] >= c[1] ? p.up : p.down) + '38' })));

    const roleColor: Record<string, string> = { trend: p.s3, bull: p.upInk, bear: p.downInk, band: p.s1, mid: p.faint, fast: p.s1, slow: p.s2 };
    for (const l of a.lines) {
      const s = chart.addSeries(LineSeries, {
        color: roleColor[l.role] || p.s4, lineWidth: l.role === 'band' || l.role === 'mid' ? 1 : 2,
        lineStyle: l.role === 'mid' ? LineStyle.Dashed : LineStyle.Solid,
        priceLineVisible: false, lastValueVisible: false, crosshairMarkerVisible: false
      });
      s.setData(l.points.map(([t, v]) => ({ time: local(t), value: v })));
    }

    a.panes.forEach((pane, i) => {
      const s = chart.addSeries(LineSeries, { color: p.s2, lineWidth: 2, priceLineVisible: false, lastValueVisible: true }, i + 1);
      s.setData(pane.points.map(([t, v]) => ({ time: local(t), value: v })));
      pane.levels.forEach(lv => s.createPriceLine({ price: lv, color: p.faint, lineStyle: LineStyle.Dashed, lineWidth: 1, axisLabelVisible: true, title: '' }));
    });
    chart.panes().forEach((pn, i) => i > 0 && pn.setHeight(110));

    const toneColor = { up: p.upInk, down: p.downInk, primary: p.primary, faint: p.faint };
    for (const lv of levels) {
      candles.createPriceLine({ price: lv.price, color: toneColor[lv.tone], lineWidth: 1, lineStyle: lv.dashed === false ? LineStyle.Solid : LineStyle.Dashed, axisLabelVisible: true, title: lv.label });
    }

    const tf = TF_SEC[a.timeframe] || 3600;
    const first = a.candles[0]?.[0] ?? 0;
    const markers: SeriesMarker<Time>[] = [];
    for (const s of a.signals) {
      markers.push(s.kind === 'long_entry'
        ? { time: local(s.time), position: 'belowBar', color: p.upInk, shape: 'arrowUp', text: '' }
        : { time: local(s.time), position: 'aboveBar', color: p.downInk, shape: 'arrowDown', text: '' });
    }
    for (const f of a.fills) {
      const t = Math.floor(new Date(f.time).getTime() / 1000 / tf) * tf;
      if (t < first) continue;
      const long = f.side === 'long';
      const isEntry = f.kind === 'entry';
      markers.push({
        time: local(t), position: (isEntry ? long : !long) ? 'belowBar' : 'aboveBar', shape: 'circle',
        color: isEntry ? p.primary : p.ink, text: isEntry ? (long ? 'Buy' : 'Sell') : 'Exit'
      });
    }
    markers.sort((x, y) => (x.time as number) - (y.time as number));
    createSeriesMarkers(candles, markers);

    if (focus) {
      chart.timeScale().setVisibleRange({ from: local(focus.from - tf * 30), to: local(focus.to + tf * 12) });
    } else {
      chart.timeScale().setVisibleLogicalRange({ from: Math.max(0, data.length - 110), to: data.length + 4 });
    }

    chart.subscribeCrosshairMove(param => {
      const d = param.seriesData.get(candles) as { open: number; high: number; low: number; close: number } | undefined;
      setHover(d ? { o: d.open, h: d.high, l: d.low, c: d.close } : null);
    });
    return () => { chart.remove(); chartRef.current = null; };
  }, [a, levels, focus, themeKey]);

  const last = a.candles[a.candles.length - 1];
  const ohlc = hover || (last ? { o: last[1], h: last[2], l: last[3], c: last[4] } : null);
  const paneH = a.panes.length * 110;
  return (
    <div style={{ position: 'relative' }}>
      <div className="chart-legend">
        {ohlc && (
          <span className="ohlc num">
            O {price(ohlc.o)} H {price(ohlc.h)} L {price(ohlc.l)} C {price(ohlc.c)}
          </span>
        )}
        {a.lines.filter((l, i, arr) => arr.findIndex(x => x.name.trim() === l.name.trim()) === i).map(l => (
          <span key={l.name}><i style={{ background: `var(${({ trend: '--series-3', bull: '--up', bear: '--down', band: '--series-1', mid: '--ink-3', fast: '--series-1', slow: '--series-2' } as Record<string, string>)[l.role] || '--series-4'})` }} />{l.name.trim()}</span>
        ))}
      </div>
      <div ref={el} style={{ height: height + paneH }} />
    </div>
  );
}
