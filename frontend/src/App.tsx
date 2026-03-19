import { useState } from "react";
import "./index.css";
import Heatmap from "./components/Heatmap";
import QuickLog from "./components/QuickLog";

export default function App() {
  const [heatmapRefreshKey, setHeatmapRefreshKey] = useState(0);

  return (
    <div className="app-shell">
      <Heatmap refreshKey={heatmapRefreshKey} />
      <QuickLog onSaveSuccess={() => setHeatmapRefreshKey((current) => current + 1)} />
    </div>
  );
}
