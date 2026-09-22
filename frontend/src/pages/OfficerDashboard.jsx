import { useEffect, useState } from "react";
import api from "../lib/api";
import Navbar from "../components/Navbar";
import BandBadge from "../components/BandBadge";
import FraudBadge from "../components/FraudBadge";

function OfficerDashboard() {
  const [applications, setApplications] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [suggestedTerms, setSuggestedTerms] = useState(null);
  const [decisionForm, setDecisionForm] = useState({ interest_rate: "", final_term_days: "" });
  const [decisionError, setDecisionError] = useState("");
  const [decisionResult, setDecisionResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const loadApplications = async () => {
    try {
      const res = await api.get("/loans/all");
      setApplications(res.data);
    } catch {
      setApplications([]);
    }
  };

  useEffect(() => {
    loadApplications();
  }, []);

  const handleExpand = async (app) => {
    if (expandedId === app.id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(app.id);
    setDecisionResult(null);
    setDecisionError("");
    setDecisionForm({ interest_rate: "", final_term_days: app.term_days });
    try {
      const res = await api.get(`/loans/${app.id}/suggested-terms`);
      setSuggestedTerms(res.data);
    } catch {
      setSuggestedTerms(null);
    }
  };

  const handleDecision = async (applicationId, decision) => {
    setDecisionError("");
    setSubmitting(true);
    try {
      const body = { decision };
      if (decision === "approved") {
        body.interest_rate = Number(decisionForm.interest_rate);
        body.final_term_days = Number(decisionForm.final_term_days);
      }
      const res = await api.post(`/loans/${applicationId}/decision`, body);
      setDecisionResult(res.data);
      await loadApplications();
    } catch (err) {
      setDecisionError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-cream-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
        <h1 className="text-lg font-semibold text-indigo-950 mb-5">Loan applications</h1>

        {applications.length === 0 ? (
          <p className="text-gray-400 text-sm">No applications yet.</p>
        ) : (
          <div className="space-y-3">
            {applications.map((app) => (
              <div key={app.id} className="bg-white rounded-2xl shadow-sm border border-gray-100">
                <button
                  onClick={() => handleExpand(app)}
                  className="w-full flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 px-4 sm:px-5 py-4 text-left"
                >
                  <div>
                    <div className="font-medium text-indigo-950">
                      #{app.id} — {app.purpose} — {app.requested_amount}
                    </div>
                    <div className="text-sm text-gray-400">
                      {app.term_days} days · {app.has_guarantor ? "Has guarantor" : "No guarantor"} · {app.status}
                    </div>
                  </div>
                  <div className="flex gap-2 flex-wrap">
                    <BandBadge band={app.risk_band} />
                    <BandBadge band={app.stress_band} />
                    <FraudBadge level={app.fraud_risk_level} />
                  </div>
                </button>

                  {expandedId === app.id && (
                  <div className="border-t border-gray-100 px-4 sm:px-5 py-4 space-y-4">
                    {app.fraud_flags && app.fraud_flags.length > 0 && (
                      <div className="bg-red-50 border border-red-100 rounded-xl p-4 text-sm">
                        <div className="font-medium text-red-800 mb-1">Fraud flags</div>
                        <ul className="text-red-700 space-y-1">
                          {app.fraud_flags.map((f, i) => (
                            <li key={i}>• {f}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {suggestedTerms && (
                      <div className="bg-cream-50 rounded-xl p-4 text-sm">
                        <div className="font-medium text-indigo-950 mb-1">Suggested terms</div>
                        <div className="text-gray-600">
                          Rate range: {suggestedTerms.suggested_interest_rate_range.min}% –{" "}
                          {suggestedTerms.suggested_interest_rate_range.max}%
                        </div>
                        <div className="text-gray-400 text-xs mt-1">{suggestedTerms.note}</div>
                      </div>
                    )}

                    {app.status === "pending" ? (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <input
                          type="number"
                          placeholder="Final interest rate (%)"
                          value={decisionForm.interest_rate}
                          onChange={(e) => setDecisionForm({ ...decisionForm, interest_rate: e.target.value })}
                          className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                        />
                        <input
                          type="number"
                          placeholder="Final term (days)"
                          value={decisionForm.final_term_days}
                          onChange={(e) => setDecisionForm({ ...decisionForm, final_term_days: e.target.value })}
                          className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                        />
                        {decisionError && (
                          <div className="sm:col-span-2 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                            {decisionError}
                          </div>
                        )}
                        <div className="sm:col-span-2 flex gap-3">
                          <button
                            onClick={() => handleDecision(app.id, "approved")}
                            disabled={submitting}
                            className="flex-1 bg-indigo-900 hover:bg-indigo-800 text-white font-medium py-2.5 rounded-lg transition disabled:opacity-60"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleDecision(app.id, "rejected")}
                            disabled={submitting}
                            className="flex-1 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2.5 rounded-lg transition disabled:opacity-60"
                          >
                            Reject
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-sm text-gray-500">Already {app.status}.</div>
                    )}

                    {decisionResult && (
                      <div className="bg-green-50 border border-green-100 rounded-lg px-4 py-3 text-sm text-green-800">
                        {decisionResult.message}
                        {decisionResult.amount_due && (
                          <> — amount due {decisionResult.amount_due} on{" "}
                            {new Date(decisionResult.due_date).toLocaleDateString()}</>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default OfficerDashboard;