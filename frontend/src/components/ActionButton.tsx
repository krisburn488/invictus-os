import type { LucideIcon } from "lucide-react";

type ActionButtonProps = {
  title: string;
  description: string;
  icon: LucideIcon;
  onClick: () => void;
};

export function ActionButton({ title, description, icon: Icon, onClick }: ActionButtonProps) {
  return (
    <button className="action-button" type="button" onClick={onClick}>
      <span className="action-button__icon" aria-hidden="true">
        <Icon />
      </span>
      <span>
        <strong>{title}</strong>
        <span>{description}</span>
      </span>
    </button>
  );
}
