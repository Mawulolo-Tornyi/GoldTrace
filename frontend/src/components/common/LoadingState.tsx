import {
  LoaderCircle,
} from "lucide-react";

export function LoadingState() {
  return (
    <div className="route-loading">
      <LoaderCircle
        size={25}
      />

      <span>
        Loading GoldTrace module...
      </span>
    </div>
  );
}
