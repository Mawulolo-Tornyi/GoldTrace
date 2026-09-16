import { create } from "zustand";

import {
  persist,
} from "zustand/middleware";

export type ThemeMode =
  | "dark"
  | "light";

export type TimeRange =
  | "LIVE"
  | "5_MIN"
  | "15_MIN"
  | "1_HOUR"
  | "6_HOURS"
  | "24_HOURS"
  | "7_DAYS";

interface SettingsStore {
  theme: ThemeMode;

  notificationSounds: boolean;

  autoFocusCritical: boolean;

  presentationMode: boolean;

  defaultTimeRange: TimeRange;

  setTheme:
    (theme: ThemeMode) => void;

  setNotificationSounds:
    (enabled: boolean) => void;

  setAutoFocusCritical:
    (enabled: boolean) => void;

  setPresentationMode:
    (enabled: boolean) => void;

  setDefaultTimeRange:
    (range: TimeRange) => void;

  resetSettings:
    () => void;
}

const defaults = {
  theme: "dark" as ThemeMode,

  notificationSounds: false,

  autoFocusCritical: false,

  presentationMode: false,

  defaultTimeRange:
    "LIVE" as TimeRange,
};

export const useSettingsStore =
  create<SettingsStore>()(
    persist(
      (set) => ({
        ...defaults,

        setTheme:
          (theme) =>
            set({
              theme,
            }),

        setNotificationSounds:
          (notificationSounds) =>
            set({
              notificationSounds,
            }),

        setAutoFocusCritical:
          (autoFocusCritical) =>
            set({
              autoFocusCritical,
            }),

        setPresentationMode:
          (presentationMode) =>
            set({
              presentationMode,
            }),

        setDefaultTimeRange:
          (defaultTimeRange) =>
            set({
              defaultTimeRange,
            }),

        resetSettings:
          () =>
            set({
              ...defaults,
            }),
      }),

      {
        name:
          "goldtrace-ui-settings",
      }
    )
  );
