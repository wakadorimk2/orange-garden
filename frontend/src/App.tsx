import "./index.css";
import Heatmap from "./components/Heatmap";
import QuickLog from "./components/QuickLog";

export default function App() {
  return (
    <div className="app-shell">
      <Heatmap />
      <QuickLog />
    </div>
  );
}
