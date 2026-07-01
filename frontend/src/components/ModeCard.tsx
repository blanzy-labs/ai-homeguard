type ModeCardProps = {
  title: string;
  description: string;
  status: string;
  disabled?: boolean;
  onSelect?: () => void;
};

export function ModeCard({ title, description, status, disabled = false, onSelect }: ModeCardProps) {
  return (
    <button className="mode-card" type="button" disabled={disabled} onClick={onSelect}>
      <span>{status}</span>
      <strong>{title}</strong>
      <p>{description}</p>
    </button>
  );
}
