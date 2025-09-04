import './card.css';

export function Card({ title, variant = 'default', children, toolbar, footer }) {
  return (
    <article className={`aa-card aa-${variant}`}>
      {(title || toolbar) && (
        <header className="aa-card-head">
          {title && <h3 className="aa-card-title">{title}</h3>}
          {toolbar && <div className="aa-card-tools">{toolbar}</div>}
        </header>
      )}
      <div className="aa-card-body">{children}</div>
      {footer && <footer className="aa-card-foot">{footer}</footer>}
    </article>
  );
}
