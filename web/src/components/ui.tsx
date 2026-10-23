import { useEffect, useId, useRef, type ReactNode } from 'react';
import CountUp from './rb/CountUp/CountUp';
import { coin } from '../lib/format';

export function Icon({ name, fill, className = '', label }: { name: string; fill?: boolean; className?: string; label?: string }) {
  return (
    <span className={`icon${fill ? ' fill' : ''} ${className}`} aria-hidden={label ? undefined : true} aria-label={label} role={label ? 'img' : undefined}>
      {name}
    </span>
  );
}

type BtnKind = 'filled' | 'tonal' | 'outlined' | 'text' | 'danger' | 'danger-tonal' | 'ghost';

export function Btn({
  kind = 'filled', icon, children, busy, small, iconOnly, title, ...rest
}: {
  kind?: BtnKind; icon?: string; children?: ReactNode; busy?: boolean; small?: boolean; iconOnly?: boolean; title?: string;
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      className={`btn ${kind}${small ? ' sm' : ''}${iconOnly ? ' icon-only' : ''}`}
      title={title}
      aria-label={iconOnly ? title : undefined}
      aria-busy={busy || undefined}
      {...rest}
      disabled={rest.disabled || busy}
    >
      {busy ? <Icon name="progress_activity" className="spin" /> : icon ? <Icon name={icon} /> : null}
      {!iconOnly && children}
    </button>
  );
}

export function Chip({ tone = '', icon, children, title }: { tone?: string; icon?: string; children: ReactNode; title?: string }) {
  return (
    <span className={`chip ${tone}`} title={title}>
      {icon && <Icon name={icon} fill />}
      {children}
    </span>
  );
}

export function Coin({ symbol, size }: { symbol: string; size?: number }) {
  const c = coin(symbol);
  return (
    <span className={`coin${c.length >= 4 ? ' long-ticker' : ''}`} style={size ? { width: size, height: size } : undefined} aria-hidden>
      {c.length > 4 ? c.slice(0, 3) : c}
    </span>
  );
}

export function SideTag({ side }: { side: string }) {
  return (
    <span className={`side-tag ${side}`}>
      <Icon name={side === 'short' ? 'south_east' : 'north_east'} />
      {side === 'short' ? 'Short' : 'Long'}
    </span>
  );
}

/** Money with an odometer roll when the value changes (React Bits CountUp). */
export function Money({ value, signed = true, className = '' }: { value: number; signed?: boolean; className?: string }) {
  const sign = !signed ? (value < 0 ? '−' : '') : value > 0 ? '+' : value < 0 ? '−' : '';
  return (
    <span className={`num ${className}`}>
      <CountUp to={Math.abs(value)} decimals={2} separator="," prefix={`${sign}$`} mode="roll" duration={0.9} trigger="load" />
    </span>
  );
}

export function Empty({ icon, title, children }: { icon: string; title: string; children?: ReactNode }) {
  return (
    <div className="empty">
      <Icon name={icon} />
      <h4>{title}</h4>
      {children && <p>{children}</p>}
    </div>
  );
}

export function Skeleton({ h = 16, w = '100%', r }: { h?: number; w?: number | string; r?: number }) {
  return <div className="skel" style={{ height: h, width: w, borderRadius: r }} />;
}

export function Switch({ checked, onChange, danger, label, disabled }: { checked: boolean; onChange: (v: boolean) => void; danger?: boolean; label: string; disabled?: boolean }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      className={`switch${danger ? ' danger' : ''}`}
      disabled={disabled}
      onClick={() => onChange(!checked)}
    />
  );
}

export function Segmented<T extends string>({ value, options, onChange, label }: { value: T; options: { value: T; label: string; icon?: string }[]; onChange: (v: T) => void; label: string }) {
  return (
    <div className="segmented" role="group" aria-label={label}>
      {options.map(o => (
        <button key={o.value} type="button" aria-pressed={o.value === value} onClick={() => onChange(o.value)}>
          {o.value === value && <Icon name="check" />}
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function FilterChip({ on, onClick, children, count, icon }: { on: boolean; onClick: () => void; children: ReactNode; count?: number; icon?: string }) {
  return (
    <button type="button" className="filter-chip" aria-pressed={on} onClick={onClick}>
      {on ? <Icon name="check" /> : icon ? <Icon name={icon} /> : null}
      {children}
      {count !== undefined && <span className="count num">{count}</span>}
    </button>
  );
}

/** Native <dialog>: focus trap, Esc and backdrop handled by the browser. */
export function Dialog({ open, onClose, icon, title, children, actions }: { open: boolean; onClose: () => void; icon?: string; title: string; children: ReactNode; actions: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (open && !d.open) d.showModal();
    if (!open && d.open) d.close();
  }, [open]);
  return (
    <dialog
      ref={ref}
      className="dlg"
      onClose={onClose}
      onClick={e => { if (e.target === ref.current) onClose(); }}
      aria-labelledby={titleId}
    >
      <div className="dlg-in">
        {icon && <Icon name={icon} className="hero-icon" />}
        <h3 id={titleId}>{title}</h3>
        <div className="body">{children}</div>
        <div className="dlg-actions">{actions}</div>
      </div>
    </dialog>
  );
}
