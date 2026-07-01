import type { Finding } from "../api/client";
import { evidenceSourceLabel } from "./reportLabels";

type EvidenceSourceBadgeProps = {
  finding: Finding;
};

export function EvidenceSourceBadge({ finding }: EvidenceSourceBadgeProps) {
  return <span className="source-badge">{evidenceSourceLabel(finding)}</span>;
}
