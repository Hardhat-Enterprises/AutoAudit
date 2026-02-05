import React from "react";

const stats = [
  { value: "10K+", label: "Organizations Trust Us" },
  { value: "99.9%", label: "Compliance Rate" },
  { value: "24/7", label: "Automated Monitoring" },
  { value: "500M+", label: "Security Events Analyzed" },
];

const StatsSection = () => {
  return (
    <section className="landing-stats" aria-label="Platform statistics">
      <div className="stats-grid">
        {stats.map((stat) => (
          <article key={stat.label} className="stat-card">
            <div className="stat-number">{stat.value}</div>
            <p className="stat-label">{stat.label}</p>
          </article>
        ))}
      </div>
    </section>
  );
};

export default StatsSection;
