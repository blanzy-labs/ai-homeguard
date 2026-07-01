type ModeCardProps = {
  title: string;
  description: string;
  status: string;
  variant?: "default" | "recommended" | "advanced";
  disabled?: boolean;
  onSelect?: () => void;
};

export function ModeCard({ title, description, status, variant = "default", disabled = false, onSelect }: ModeCardProps) {
  return (
    <button className={`mode-card mode-card--${variant}`} type="button" disabled={disabled} onClick={onSelect}>
      <span>{status}</span>
      <strong>{title}</strong>
      <p>{description}</p>
    </button>
  );
}
