import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import api from "../lib/api";
import Navbar from "../components/Navbar";

const LINE_COLORS = ["#312e81", "#f59e0b", "#059669", "#dc2626", "#0891b2"];

function Forecast() {
  const [horizon, setHorizon] = useState(6);
  const [baseline, setBaseline] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const [scenarios, setScenarios] = useState([
    { name: "baseline", income_growth_rate: 0, shock_month: "", shock_pct: 0, extra_monthly_expense: 0 },
  ]);
  const [comparisonData, setComparisonData] = useState(null);
  const [comparing, setComparing] = useState(false);

  const loadBaseline = async (months) => {
    setError("");
    setLoading(true);
    try {
      const res = await api.get(`/simulation/forecast?horizon_months=${months}`);
      setBaseline(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load forecast.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBaseline(horizon);
  }, []);

  const addScenario = () => {
    setScenarios([
      ...scenarios,
      { name: `scenario ${scenarios.length + 1}`, income_growth_rate: 0, shock_month: "", shock_pct: 0, extra_monthly_expense: 0 },
    ]);
  };

  const updateScenario = (index, field, value) => {
    const updated = [...scenarios];
    updated[index] = { ...updated[index], [field]: value };
    setScenarios(updated);
  };

  const removeScenario = (index) => {
    setScenarios(scenarios.filter((_, i) => i !== index));
  };

  const runComparison = async () => {
    setComparing(true);
    setError("");
    try {
      const payload = {
        horizon_months: horizon,
        scenarios: scenarios.map((s) => ({
          name: s.name,
          income_growth_rate: Number(s.income_growth_rate) || 0,
          shock_month: s.shock_month === "" ? null : Number(s.shock_month),
          shock_pct: Number(s.shock_pct) || 0,
          extra_monthly_expense: Number(s.extra_monthly_expense) || 0,
        })),
      };
      const res = await api.post("/simulation/compare", payload);
      setComparisonData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not run comparison.");
    } finally {
      setComparing(false);
    }
  };

  const chartData = (() => {
    if (comparisonData) {
      const months = Object.values(comparisonData.scenarios)[0]?.length || 0;
      return Array.from({ length: months }, (_, i) => {
        const row = { month: i + 1 };
        for (const [name, series] of Object.entries(comparisonData.scenarios)) {
          row[name] = series[i]?.cumulative_balance;
        }
        return row;
      });
    }
    if (baseline) {
      return baseline.months.map((m) => ({ month: m.month, baseline: m.cumulative_balance }));
    }
    return [];
  })();

  const seriesNames = comparisonData ? Object.keys(comparisonData.scenarios) : ["baseline"];

  return (
    <div className="min-h-screen bg-cream-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-10 space-y-6 sm:space-y-8">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-5">
            <h1 className="text-lg font-semibold text-indigo-950">Cash-flow forecast</h1>
            <div className="flex items-center gap-2 text-sm">
              <label className="text-gray-500">Horizon:</label>
              <select
                value={horizon}
                onChange={(e) => {
                  const months = Number(e.target.value);
                  setHorizon(months);
                  setComparisonData(null);
                  loadBaseline(months);
                }}
                className="border border-gray-300 rounded-lg px-3 py-1.5"
              >
                <option value={3}>3 months</option>
                <option value={6}>6 months</option>
                <option value={12}>12 months</option>
              </select>
            </div>
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 mb-4">
              {error}
            </div>
          )}

          {loading ? (
            <p className="text-gray-400 text-sm">Loading forecast...</p>
          ) : chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280} minWidth={0}>
              <LineChart data={chartData} margin={{ left: -10, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f0ee" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} label={{ value: "Month", position: "insideBottom", offset: -5, fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} width={50} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                {seriesNames.map((name, i) => (
                  <Line
                    key={name}
                    type="monotone"
                    dataKey={name}
                    stroke={LINE_COLORS[i % LINE_COLORS.length]}
                    strokeWidth={2}
                    dot={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-sm">No data to show yet.</p>
          )}
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-5">
            <h2 className="text-lg font-semibold text-indigo-950">Compare scenarios</h2>
            <button onClick={addScenario} className="text-sm text-indigo-700 font-medium hover:underline self-start sm:self-auto">
              + Add scenario
            </button>
          </div>

          <div className="space-y-4">
            {scenarios.map((s, i) => (
              <div key={i} className="border border-gray-100 rounded-xl p-3 sm:p-0 sm:border-0">
                <div className="flex items-center justify-between sm:hidden mb-2">
                  <span className="text-xs font-medium text-gray-400">Scenario {i + 1}</span>
                  {scenarios.length > 1 && (
                    <button onClick={() => removeScenario(i)} className="text-gray-400 hover:text-red-500 text-xs">
                      Remove
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 items-center">
                  <input
                    placeholder="Name"
                    value={s.name}
                    onChange={(e) => updateScenario(i, "name", e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  />
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Growth rate (e.g. 0.02)"
                    value={s.income_growth_rate}
                    onChange={(e) => updateScenario(i, "income_growth_rate", e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  />
                  <input
                    type="number"
                    placeholder="Shock month"
                    value={s.shock_month}
                    onChange={(e) => updateScenario(i, "shock_month", e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  />
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Shock % (0-1)"
                    value={s.shock_pct}
                    onChange={(e) => updateScenario(i, "shock_pct", e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  />
                  <div className="flex gap-2">
                    <input
                      type="number"
                      placeholder="Extra expense"
                      value={s.extra_monthly_expense}
                      onChange={(e) => updateScenario(i, "extra_monthly_expense", e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-full"
                    />
                    {scenarios.length > 1 && (
                      <button onClick={() => removeScenario(i)} className="hidden sm:block text-gray-400 hover:text-red-500 px-1">
                        ✕
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={runComparison}
            disabled={comparing}
            className="mt-5 w-full sm:w-auto bg-indigo-900 hover:bg-indigo-800 text-white font-medium px-5 py-2.5 rounded-lg text-sm transition disabled:opacity-60"
          >
            {comparing ? "Running..." : "Run comparison"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Forecast;