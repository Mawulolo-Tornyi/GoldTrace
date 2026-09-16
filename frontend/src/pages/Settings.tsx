import {
  BellRing,
  Focus,
  MonitorCog,
  Moon,
  RotateCcw,
  Sun,
} from "lucide-react";

import { useSettingsStore } from "../store/settingsStore";

export default function Settings() {
  const theme =
    useSettingsStore(
      (state) =>
        state.theme
    );

  const notificationSounds =
    useSettingsStore(
      (state) =>
        state.notificationSounds
    );

  const autoFocusCritical =
    useSettingsStore(
      (state) =>
        state.autoFocusCritical
    );

  const presentationMode =
    useSettingsStore(
      (state) =>
        state.presentationMode
    );

  const defaultTimeRange =
    useSettingsStore(
      (state) =>
        state.defaultTimeRange
    );

  const setTheme =
    useSettingsStore(
      (state) =>
        state.setTheme
    );

  const setNotificationSounds =
    useSettingsStore(
      (state) =>
        state.setNotificationSounds
    );

  const setAutoFocusCritical =
    useSettingsStore(
      (state) =>
        state.setAutoFocusCritical
    );

  const setPresentationMode =
    useSettingsStore(
      (state) =>
        state.setPresentationMode
    );

  const setDefaultTimeRange =
    useSettingsStore(
      (state) =>
        state.setDefaultTimeRange
    );

  const resetSettings =
    useSettingsStore(
      (state) =>
        state.resetSettings
    );

  return (
    <div>
      <div className="page-heading">
        <div>
          <span className="eyebrow">
            OPERATOR
            PREFERENCES
          </span>

          <h2>
            Settings
          </h2>

          <p>
            Interface preferences only.
            Detection and ML thresholds
            remain controlled by the
            backend.
          </p>
        </div>
      </div>

      <div className="settings-section">
        <div className="settings-section-heading">
          <MonitorCog
            size={18}
          />

          <div>
            <strong>
              Appearance
            </strong>

            <span>
              GoldTrace command-center
              appearance.
            </span>
          </div>
        </div>

        <div className="theme-options">
          <button
            className={
              theme === "dark"
                ? "theme-option active"
                : "theme-option"
            }
            onClick={() =>
              setTheme(
                "dark"
              )
            }
          >
            <Moon
              size={18}
            />

            <strong>
              Dark
            </strong>

            <span>
              Command center
            </span>
          </button>

          <button
            className={
              theme === "light"
                ? "theme-option active"
                : "theme-option"
            }
            onClick={() =>
              setTheme(
                "light"
              )
            }
          >
            <Sun
              size={18}
            />

            <strong>
              Light
            </strong>

            <span>
              Daylight view
            </span>
          </button>
        </div>
      </div>

      <div className="settings-section">
        <div className="settings-row">
          <div className="settings-row-info">
            <BellRing
              size={18}
            />

            <div>
              <strong>
                Critical alert
                sound
              </strong>

              <span>
                Play one notification
                sound for a new
                critical event.
              </span>
            </div>
          </div>

          <button
            className={
              notificationSounds
                ? "switch-control enabled"
                : "switch-control"
            }
            onClick={() =>
              setNotificationSounds(
                !notificationSounds
              )
            }
            aria-pressed={
              notificationSounds
            }
          >
            <span />
          </button>
        </div>

        <div className="settings-row">
          <div className="settings-row-info">
            <Focus
              size={18}
            />

            <div>
              <strong>
                Auto-focus critical
                events
              </strong>

              <span>
                Allow the GIS view to
                focus a newly received
                critical zone.
              </span>
            </div>
          </div>

          <button
            className={
              autoFocusCritical
                ? "switch-control enabled"
                : "switch-control"
            }
            onClick={() =>
              setAutoFocusCritical(
                !autoFocusCritical
              )
            }
            aria-pressed={
              autoFocusCritical
            }
          >
            <span />
          </button>
        </div>

        <div className="settings-row">
          <div className="settings-row-info">
            <MonitorCog
              size={18}
            />

            <div>
              <strong>
                Presentation Mode
              </strong>

              <span>
                Larger monitoring
                elements with reduced
                navigation clutter for
                demonstrations.
              </span>
            </div>
          </div>

          <button
            className={
              presentationMode
                ? "switch-control enabled"
                : "switch-control"
            }
            onClick={() =>
              setPresentationMode(
                !presentationMode
              )
            }
            aria-pressed={
              presentationMode
            }
          >
            <span />
          </button>
        </div>
      </div>

      <div className="settings-section">
        <div className="settings-select-row">
          <div>
            <strong>
              Default chart time
              range
            </strong>

            <span>
              Historical periods will
              later request aggregated
              backend data.
            </span>
          </div>

          <select
            value={
              defaultTimeRange
            }
            onChange={(event) =>
              setDefaultTimeRange(
                event.target
                  .value as
                  typeof defaultTimeRange
              )
            }
          >
            <option value="LIVE">
              Live
            </option>

            <option value="5_MIN">
              5 minutes
            </option>

            <option value="15_MIN">
              15 minutes
            </option>

            <option value="1_HOUR">
              1 hour
            </option>

            <option value="6_HOURS">
              6 hours
            </option>

            <option value="24_HOURS">
              24 hours
            </option>

            <option value="7_DAYS">
              7 days
            </option>
          </select>
        </div>
      </div>

      <button
        className="reset-settings-button"
        onClick={
          resetSettings
        }
      >
        <RotateCcw
          size={15}
        />

        Reset interface settings
      </button>
    </div>
  );
}
