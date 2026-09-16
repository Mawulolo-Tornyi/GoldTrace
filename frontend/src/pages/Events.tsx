import {
  ChevronRight,
  Search,
} from "lucide-react";

import {
  useMemo,
  useState,
} from "react";

import { Link } from "react-router-dom";

import { useLiveStore } from "../store/liveStore";

import {
  percent,
  riskClass,
} from "../utils/formatters";

export default function Events() {
  const events = useLiveStore(
    (state) => state.events
  );

  const [search, setSearch] =
    useState("");

  const [risk, setRisk] =
    useState("ALL");

  const filtered =
    useMemo(
      () =>
        events.filter(
          (event) => {
            const searchMatch =
              event.event_id
                .toLowerCase()
                .includes(
                  search.toLowerCase()
                ) ||
              event.prediction
                .toLowerCase()
                .includes(
                  search.toLowerCase()
                ) ||
              event.zone
                .toLowerCase()
                .includes(
                  search.toLowerCase()
                );

            const riskMatch =
              risk === "ALL" ||
              event.risk === risk;

            return (
              searchMatch &&
              riskMatch
            );
          }
        ),
      [
        events,
        search,
        risk,
      ]
    );

  return (
    <div>
      <div className="page-heading">
        <div>
          <span className="eyebrow">
            DETECTION HISTORY
          </span>

          <h2>
            Events
          </h2>

          <p>
            Review GoldTrace detections,
            classifications and investigation zones.
          </p>
        </div>
      </div>

      <div className="filter-bar">
        <label className="search-box">
          <Search size={15} />

          <input
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
            placeholder="Search event, prediction or zone..."
          />
        </label>

        <select
          value={risk}
          onChange={(event) =>
            setRisk(
              event.target.value
            )
          }
        >
          <option value="ALL">
            All risks
          </option>

          <option value="LOW">
            Low
          </option>

          <option value="MEDIUM">
            Medium
          </option>

          <option value="HIGH">
            High
          </option>

          <option value="CRITICAL">
            Critical
          </option>
        </select>
      </div>

      <div className="table-card">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>
                  EVENT
                </th>

                <th>
                  TIME
                </th>

                <th>
                  PREDICTION
                </th>

                <th>
                  RISK
                </th>

                <th>
                  CONFIDENCE
                </th>

                <th>
                  ZONE
                </th>

                <th>
                  DURATION
                </th>

                <th>
                  STATUS
                </th>

                <th />
              </tr>
            </thead>

            <tbody>
              {filtered.map(
                (event) => (
                  <tr
                    key={
                      event.event_id
                    }
                  >
                    <td>
                      <strong>
                        {
                          event.event_id
                        }
                      </strong>
                    </td>

                    <td>
                      {new Date(
                        event.timestamp
                      ).toLocaleString()}
                    </td>

                    <td>
                      {
                        event.prediction
                      }
                    </td>

                    <td>
                      <span
                        className={`risk-badge ${riskClass(
                          event.risk
                        )}`}
                      >
                        {
                          event.risk
                        }
                      </span>
                    </td>

                    <td>
                      {percent(
                        event.confidence
                      )}
                    </td>

                    <td>
                      {
                        event.zone
                      }
                    </td>

                    <td>
                      {
                        event.duration_seconds
                      }
                      s
                    </td>

                    <td>
                      {
                        event.status
                      }
                    </td>

                    <td>
                      <Link
                        to={`/events/${event.event_id}`}
                        className="table-action"
                      >
                        View

                        <ChevronRight
                          size={14}
                        />
                      </Link>
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>

          {filtered.length ===
            0 && (
            <div className="table-empty">
              No matching GoldTrace events.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
