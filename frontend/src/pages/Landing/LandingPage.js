import React from "react";
import {Link} from "react-router-dom";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface-1 text-text-strong font-body">

      {/*Landing page*/}
      <header className="relative p-6 flex items-center justify-between">

        {/*Logo - Is unchanged, using hte png file from system*/}
        <div className="absolute top-6 left-6">
          <img
            src="/logo.png"
            alt="AutoAudit logo"
            className="w-40 rounded-card shadow-elev-1"
          />
        </div>

        <nav className="ml-auto flex items-center gap-6">
          <button className="text-text-strong font-semibold text-lg opacity-90 hover:bg-accent-navy hover:rounded-card px-4 py-2">
            Features
          </button>

          <button className="text-text-strong font-semibold text-lg opacity-90 hover:bg-accent-navy hover:rounded-card px-4 py-2">
            Pricing
          </button>

          <Link
            to="/login"
            className="px-4 py-2 bg-accent-teal text-surface-1 font-semibold rounded-card hover:bg-accent-teal/80"
          >
            Sign in
          </Link>
        </nav>
      </header>

      {/*Hero Class*/}
      <section className="min-h-[80vh] flex items-center pl-10 mt-20">
        <div className="max-w-2xl">

          <p className="text-accent-teal font-bold uppercase text-sm mb-2">
            Continuous Security Evidence
          </p>

          <h1 className="text-5xl font-extrabold leading-tight mb-4 font-header">
            Audit-ready security
            <br />
            without the chaos
          </h1>

          <p className="text-text-muted text-lg leading-relaxed max-w-xl mb-6">
            AutoAudit continuously collects, validates, and presents your
            security evidence so audits become routine — not stressful.
          </p>

          <div className="flex gap-4 flex-wrap">
            <Link
              to="/signup"
              className="px-5 py-3 bg-accent-teal text-surface-1 font-bold rounded-card shadow-elev-1 hover:bg-accent-teal/80"
            >
              Get started
            </Link>

            <Link
              to="/demo"
              className="px-5 py-3 border border-border-subtle text-text-strong rounded-card hover:bg-surface-2"
            >
              View demo
            </Link>
          </div>
        </div>
      </section>

    {/*Features Class*/}
      <section className="py-20">
        <div className="max-w-6xl mx-auto grid gap-6 sm:grid-cols-2 px-6">

          <FeatureCard
            title="Automated Evidence"
            text="Evidence is collected continuously and mapped to controls automatically."
          />

          <FeatureCard
            title="Audit Trails"
            text="Every change is logged with timestamps and validation status."
          />

          <FeatureCard
            title="Framework Mapping"
            text="Supports ISO 27001, SOC 2, and more out of the box."
          />

          <FeatureCard
            title="Export Ready"
            text="Generate audit-ready reports in minutes, not weeks."
          />

        </div>
      </section>

      {/*Insights and Why classes*/}
      <section className="py-16 text-center max-w-4xl mx-auto px-6">

        <p className="text-text-strong text-lg font-medium mb-4">
          Built for teams who want audits to feel boring
        </p>

        <h2 className="text-xl font-semibold mb-10">
          Why teams choose AutoAudit
        </h2>

        <div className="grid gap-8 sm:grid-cols-3">
          <WhyCard title="Less Manual Work" />
          <WhyCard title="Faster Audits" />
          <WhyCard title="Clear Evidence" />
        </div>

      </section>

    </div>
  );
}

{/*Sub compentent class*/}

function FeatureCard({ title, text }) {
  return (
    <div
      className="
        bg-surface-2
        border border-border-subtle
        rounded-card
        p-6
        shadow-elev-1
        backdrop-blur
        transition
        hover:-translate-y-1
        hover:shadow-elev-2
      "
    >
      <div className="mb-3 text-accent-teal">
       
        ●
      </div>

      <h3 className="font-extrabold mb-2">
        {title}
      </h3>

      <p className="text-text-muted text-sm leading-relaxed">
        {text}
      </p>
    </div>
  );
}

function WhyCard({ title }) {
  return (
    <div
      className="
        bg-surface-2
        border border-border-subtle
        rounded-card
        p-6
        shadow-elev-1
        transition
        hover:-translate-y-1
      "
    >
      <h3 className="font-bold mb-2">
        {title}
      </h3>

      <p className="text-text-muted text-sm">
        Designed to reduce audit fatigue and improve clarity.
      </p>
    </div>
  );
}
