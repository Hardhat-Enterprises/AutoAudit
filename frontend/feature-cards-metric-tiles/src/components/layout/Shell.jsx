import './shell.css';

export default function Shell({ children }) {
  return (
    <main className="aa-shell">
      <div className="aa-shell-inner">{children}</div>
    </main>
  );
}