import {
  Activity,
  Bell,
  BrainCircuit,
  Gauge,
  FlaskConical,
  LayoutDashboard,
  Map,
  Moon,
  RadioTower,
  Settings,
  ShieldCheck,
  Sun,
  Waves,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  NavLink,
  Outlet,
} from "react-router-dom";

import { useGoldTraceRuntime } from "../../hooks/useGoldTraceRuntime";

import { useLiveStore } from "../../store/liveStore";

import { useSettingsStore } from "../../store/settingsStore";

import { MobileNav } from "./MobileNav";

const navigation = [
  {
    to: "/",
    label: "Dashboard",
    icon: LayoutDashboard,
  },

  {
    to: "/live",
    label: "Live Monitoring",
    icon: Activity,
  },

  {
    to: "/map",
    label: "River Map",
    icon: Map,
  },

  {
    to: "/nodes",
    label: "Nodes",
    icon: RadioTower,
  },

  {
    to: "/events",
    label: "Events",
    icon: Waves,
  },

  {
    to: "/alerts",
    label: "Alerts",
    icon: Bell,
  },

  {
    to: "/models",
    label: "ML Models",
    icon: BrainCircuit,
  },

  {
    to: "/system",
    label: "System Health",
    icon: Gauge,
  },

  {
    to: "/simulator",
    label: "Simulator",
    icon: FlaskConical,
  },

  {
    to: "/settings",
    label: "Settings",
    icon: Settings,
  },
];

export function AppLayout() {
  useGoldTraceRuntime();

  const connected =
    useLiveStore(
      (state) =>
        state.connected
    );

  const demoMode =
    useLiveStore(
      (state) =>
        state.demoMode
    );

  const alerts =
    useLiveStore(
      (state) =>
        state.alerts
    );

  const theme =
    useSettingsStore(
      (state) =>
        state.theme
    );

  const setTheme =
    useSettingsStore(
      (state) =>
        state.setTheme
    );

  const presentationMode =
    useSettingsStore(
      (state) =>
        state.presentationMode
    );

  const [clock, setClock] =
    useState(
      new Date()
    );

  const activeAlerts =
    alerts.filter(
      (alert) =>
        alert.status ===
        "ACTIVE"
    ).length;

  useEffect(() => {
    const timer =
      window.setInterval(
        () => {
          setClock(
            new Date()
          );
        },
        1000
      );

    return () =>
      window.clearInterval(
        timer
      );
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme =
      theme;

    document.documentElement.dataset.presentation =
      presentationMode
        ? "true"
        : "false";
  }, [
    theme,
    presentationMode,
  ]);

  function toggleTheme() {
    setTheme(
      theme === "dark"
        ? "light"
        : "dark"
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <ShieldCheck
              size={24}
            />
          </div>

          <div>
            <strong>
              GOLDTRACE
            </strong>

            <span>
              River Intelligence
            </span>
          </div>
        </div>

        {demoMode && (
          <div className="demo-banner">
            DEMO MODE
          </div>
        )}

        <nav className="sidebar-nav">
          {navigation.map(
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
                    ? "nav-link active"
                    : "nav-link"
                }
              >
                <Icon
                  size={18}
                />

                <span>
                  {label}
                </span>
              </NavLink>
            )
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="gateway-status">
            <span
              className={
                connected
                  ? "status-dot online"
                  : "status-dot offline"
              }
            />

            <span>
              {connected
                ? "Gateway connected"
                : "Gateway disconnected"}
            </span>
          </div>

          <small>
            GoldTrace v0.2.0
          </small>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <span className="eyebrow">
              ENVIRONMENTAL
              INTELLIGENCE
            </span>

            <h1>
              GoldTrace Command Center
            </h1>
          </div>

          <div className="header-controls">
            <div className="header-clock">
              <strong>
                {clock.toLocaleTimeString(
                  [],
                  {
                    hour:
                      "2-digit",
                    minute:
                      "2-digit",
                    second:
                      "2-digit",
                  }
                )}
              </strong>

              <span>
                {clock.toLocaleDateString(
                  [],
                  {
                    day:
                      "2-digit",
                    month:
                      "short",
                    year:
                      "numeric",
                  }
                )}
              </span>
            </div>

            <div className="notification-control">
              <Bell
                size={17}
              />

              {activeAlerts >
                0 && (
                <span>
                  {activeAlerts}
                </span>
              )}
            </div>

            <button
              className="header-icon-button"
              onClick={
                toggleTheme
              }
              aria-label="Toggle theme"
              title="Toggle theme"
            >
              {theme ===
              "dark" ? (
                <Sun
                  size={17}
                />
              ) : (
                <Moon
                  size={17}
                />
              )}
            </button>

            <div
              className={
                connected
                  ? "live-pill"
                  : "offline-pill"
              }
            >
              <span
                className={
                  connected
                    ? "status-dot online"
                    : "status-dot offline"
                }
              />

              {connected
                ? "LIVE"
                : "OFFLINE"}
            </div>
          </div>
        </header>

        {!connected &&
          !demoMode && (
            <div className="connection-warning">
              LIVE CONNECTION LOST —
              attempting to reconnect
              to the GoldTrace gateway.
            </div>
          )}

        {presentationMode && (
          <div className="presentation-banner">
            PRESENTATION MODE
          </div>
        )}

        <section className="page-content">
          <Outlet />
        </section>
      </main>

      <MobileNav />
    </div>
  );
}
