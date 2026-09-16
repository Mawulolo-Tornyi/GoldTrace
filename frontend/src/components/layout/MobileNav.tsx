import {
  Activity,
  Bell,
  LayoutDashboard,
  Map,
  RadioTower,
} from "lucide-react";

import {
  NavLink,
} from "react-router-dom";

const mobileLinks = [
  {
    to: "/",
    label: "Home",
    icon: LayoutDashboard,
  },

  {
    to: "/live",
    label: "Live",
    icon: Activity,
  },

  {
    to: "/map",
    label: "Map",
    icon: Map,
  },

  {
    to: "/nodes",
    label: "Nodes",
    icon: RadioTower,
  },

  {
    to: "/alerts",
    label: "Alerts",
    icon: Bell,
  },
];

export function MobileNav() {
  return (
    <nav
      className="mobile-nav"
      aria-label="Mobile navigation"
    >
      {mobileLinks.map(
        ({
          to,
          label,
          icon: Icon,
        }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({
              isActive,
            }) =>
              isActive
                ? "mobile-nav-link active"
                : "mobile-nav-link"
            }
          >
            <Icon size={18} />

            <span>
              {label}
            </span>
          </NavLink>
        )
      )}
    </nav>
  );
}
