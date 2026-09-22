import { useEffect, useState } from "react";
import api from "../lib/api";
import Navbar from "../components/Navbar";
import HealthBadge from "../components/HealthBadge";
import BandBadge from "../components/BandBadge";

function Monitoring() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setError("");
    setLoading(true);
    try {
      const res = await api.get("/monitoring/alerts");
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load monitoring data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="min-h-screen bg-cream-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
        <h1 className="text-lg font-semibold text-indigo-950 mb-2">Loan monitoring</h1>
        <p className="text-gray-500 text-sm mb-6">
          Predicted risk at origination vs. actual repayment behavior, updated live.
        </p>

        {error && (
          <div className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-gray-400 text-sm">Loading...</p>
        ) : data && data.loans.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div className="bg-white rounded-xl border border-gray-100 p-4">
                <div className="text-2xl font-semibold text-indigo-950">{data.total}</div>
                <div className="text-sm text-gray-400">Total loans</div>
              </div>
              <div className="bg-white rounded-xl border border-gray-100 p-4">
                <div className="text-2xl font-semibold text-red-600">{data.alert_count}</div>
                <div className="text-sm text-gray-400">Active alerts</div>
              </div>
              <div className="bg-white rounded-xl border border-gray-100 p-4">
                <div className="text-2xl font-semibold text-amber-600">{data.diverged_count}</div>
                <div className="text-sm text-gray-400">Predictions diverged</div>
              </div>
            </div>

            <div className="space-y-3">
              {data.loans.map((loan) => (
                <div
                  key={loan.loan_id}
                  className={`bg-white rounded-2xl border p-4 sm:p-5 ${
                    loan.is_alert ? "border-red-200" : "border-gray-100"
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 mb-3">
                    <div>
                      <div className="font-medium text-indigo-950">
                        {loan.business_name} — {loan.purpose}
                      </div>
                      <div className="text-sm text-gray-400">
                        {loan.amount_due} due {new Date(loan.due_date).toLocaleDateString()}
                      </div>
                    </div>
                    <HealthBadge status={loan.health_status} />
                  </div>

                  <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
                    <div>
                      <span className="text-gray-400">Predicted: </span>
                      <BandBadge band={loan.predicted_risk_band} />
                      <span className="text-gray-400 ml-1">({loan.predicted_risk_score})</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Now: </span>
                      <BandBadge band={loan.dynamic_risk_band} />
                      <span className="text-gray-400 ml-1">({loan.dynamic_risk_score})</span>
                    </div>
                    {loan.prediction_diverged && (
                      <span className="text-amber-600 text-xs font-medium">Prediction diverged</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p className="text-gray-400 text-sm">No active loans to monitor yet.</p>
        )}
      </div>
    </div>
  );
}

export default Monitoring;