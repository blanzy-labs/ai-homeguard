type FeatureCardProps = {
  title: string;
  label: string;
};

export function FeatureCard({ title, label }: FeatureCardProps) {
  return (
    <article className="feature-card">
      <h3>{title}</h3>
      <p>{label}</p>
    </article>
  );
}
