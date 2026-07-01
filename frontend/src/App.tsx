import { FeatureCard } from "./components/FeatureCard";
import { StatusPanel } from "./components/StatusPanel";

const features = [
  { title: "Device Audit", label: "Coming soon" },
  { title: "Home Network Awareness", label: "Coming soon" },
  { title: "D3FEND Guidance", label: "Coming soon" },
  { title: "Plain-English Report", label: "Coming soon" },
];

export default function App() {
  return (
    <main className="app-shell">
      <section className="intro">
        <div className="brand-row">
          <span className="brand-mark" aria-hidden="true">
            HG
          </span>
          <p>Blanzy Labs AI app family</p>
        </div>
        <h1>AI HomeGuard</h1>
        <p className="subtitle">Local Home Security Audit MVP</p>
        <p className="safety-message">
          AI HomeGuard is a local-first defensive cyber hygiene tool. It does not exploit, attack,
          brute-force, packet-sniff, or scan public targets.
        </p>
        <button className="demo-button" type="button" disabled>
          Demo Mode - Coming in a later slice
        </button>
      </section>

      <section className="feature-grid" aria-label="Planned capabilities">
        {features.map((feature) => (
          <FeatureCard key={feature.title} title={feature.title} label={feature.label} />
        ))}
      </section>

      <StatusPanel />
    </main>
  );
}
