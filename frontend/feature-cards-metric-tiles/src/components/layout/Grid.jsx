import './grid.css';

export const GridContainer = ({ maxWidth='1440px', gap=24, padX=24, children }) => (
  <div className="aa-grid-container" style={{
    ['--aa-gap']: `${gap}px`,
    ['--aa-pad-x']: `${padX}px`,
    ['--aa-max-w']: maxWidth
  }}>
    {children}
  </div>
);

export const Row = ({ minH=0, children }) => (
  <section className="aa-row" style={{ ['--aa-row-min-h']: minH?`${minH}px`:'auto' }}>
    {children}
  </section>
);

export const Col = ({ span, children }) => (
  <div className="aa-col" style={{
    ['--aa-span']: span.base,
    ['--aa-span-md']: span.md ?? span.base,
    ['--aa-span-lg']: span.lg ?? span.md ?? span.base
  }}>
    {children}
  </div>
);
