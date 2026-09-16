interface Props {
  title: string;
  description: string;
}

export default function SectionPage({
  title,
  description,
}: Props) {
  return (
    <div>
      <div className="page-heading">
        <span className="eyebrow">
          GOLDTRACE
        </span>

        <h2>{title}</h2>

        <p>
          {description}
        </p>
      </div>

      <div className="module-preparing">
        <strong>
          {title}
        </strong>

        <p>
          This module is being connected in the next frontend build step.
        </p>
      </div>
    </div>
  );
}
