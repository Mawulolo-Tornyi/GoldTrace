import type { ReactNode } from "react";

interface Props {
  title: string;
  value: ReactNode;
  subtitle?: string;
  icon?: ReactNode;
  accent?: "green" | "red" | "purple";
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon,
  accent = "green",
}: Props) {
  return (
    <article className={`metric-card accent-${accent}`}>
      <div className="metric-header">
        <span>{title}</span>
        {icon}
      </div>

      <div className="metric-value">
        {value}
      </div>

      {subtitle && (
        <p className="metric-subtitle">
          {subtitle}
        </p>
      )}
    </article>
  );
}
