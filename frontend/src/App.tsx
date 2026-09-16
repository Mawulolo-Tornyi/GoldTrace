import {
  lazy,
  Suspense,
} from "react";

import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import { AppLayout } from "./components/layout/AppLayout";

import { LoadingState } from "./components/common/LoadingState";

const Dashboard =
  lazy(
    () =>
      import(
        "./pages/Dashboard"
      )
  );

const LiveMonitoring =
  lazy(
    () =>
      import(
        "./pages/LiveMonitoring"
      )
  );

const MapView =
  lazy(
    () =>
      import(
        "./pages/MapView"
      )
  );

const Nodes =
  lazy(
    () =>
      import(
        "./pages/Nodes"
      )
  );

const NodeDetails =
  lazy(
    () =>
      import(
        "./pages/NodeDetails"
      )
  );

const Events =
  lazy(
    () =>
      import(
        "./pages/Events"
      )
  );

const EventDetails =
  lazy(
    () =>
      import(
        "./pages/EventDetails"
      )
  );

const Alerts =
  lazy(
    () =>
      import(
        "./pages/Alerts"
      )
  );

const Models =
  lazy(
    () =>
      import(
        "./pages/Models"
      )
  );

const SystemHealth =
  lazy(
    () =>
      import(
        "./pages/SystemHealth"
      )
  );

const Simulator =
  lazy(
    () =>
      import(
        "./pages/Simulator"
      )
  );

const Settings =
  lazy(
    () =>
      import(
        "./pages/Settings"
      )
  );

function PageLoader({
  children,
}: {
  children:
    React.ReactNode;
}) {
  return (
    <Suspense
      fallback={
        <LoadingState />
      }
    >
      {children}
    </Suspense>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          element={
            <AppLayout />
          }
        >
          <Route
            path="/"
            element={
              <PageLoader>
                <Dashboard />
              </PageLoader>
            }
          />

          <Route
            path="/live"
            element={
              <PageLoader>
                <LiveMonitoring />
              </PageLoader>
            }
          />

          <Route
            path="/map"
            element={
              <PageLoader>
                <MapView />
              </PageLoader>
            }
          />

          <Route
            path="/nodes"
            element={
              <PageLoader>
                <Nodes />
              </PageLoader>
            }
          />

          <Route
            path="/nodes/:id"
            element={
              <PageLoader>
                <NodeDetails />
              </PageLoader>
            }
          />

          <Route
            path="/events"
            element={
              <PageLoader>
                <Events />
              </PageLoader>
            }
          />

          <Route
            path="/events/:id"
            element={
              <PageLoader>
                <EventDetails />
              </PageLoader>
            }
          />

          <Route
            path="/alerts"
            element={
              <PageLoader>
                <Alerts />
              </PageLoader>
            }
          />

          <Route
            path="/models"
            element={
              <PageLoader>
                <Models />
              </PageLoader>
            }
          />

          <Route
            path="/system"
            element={
              <PageLoader>
                <SystemHealth />
              </PageLoader>
            }
          />

          <Route
            path="/simulator"
            element={
              <PageLoader>
                <Simulator />
              </PageLoader>
            }
          />

          <Route
            path="/settings"
            element={
              <PageLoader>
                <Settings />
              </PageLoader>
            }
          />

          <Route
            path="*"
            element={
              <PageLoader>
                <Dashboard />
              </PageLoader>
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
