import { useEffect, useState } from "react";
import api from "../lib/api";
import Navbar from "../components/Navbar";
import BandBadge from "../components/BandBadge";
import HealthBadge from "../components/HealthBadge";

function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [applications, setApplications] = useState([]);

  const [profileForm, setProfileForm] = useState({
    business_name: "",
    sector: "",
    monthly_income_estimate: "",
    years_operating: "",
  });
  const [profileError, setProfileError] = useState("");
  const [profileSubmitting, setProfileSubmitting] = useState(false);

  const [showApplyForm, setShowApplyForm] = useState(false);
  const [applyForm, setApplyForm] = useState({
    requested_amount: "",
    purpose: "",
    term_days: "",
    has_guarantor: false,
  });
  const [applyError, setApplyError] = useState("");
  const [applyResult, setApplyResult] = useState(null);
  const [applySubmitting, setApplySubmitting] = useState(false);

  const [loanHealth, setLoanHealth] = useState([]);
  const [repayingId, setRepayingId] = useState(null);
  const [repayError, setRepayError] = useState("");

  const loadProfile = async () => {
    try {
      const res = await api.get("/business/profile/me");
      setProfile(res.data);
    } catch {
      setProfile(null);
    } finally {
      setProfileLoading(false);
    }
  };

  const loadApplications = async () => {
    try {
      const res = await api.get("/loans/my-applications");
      setApplications(res.data);
    } catch {
      setApplications([]);
    }
  };

  const loadLoanHealth = async () => {
    try {
      const res = await api.get("/monitoring/my-loans");
      setLoanHealth(res.data.loans);
    } catch {
      setLoanHealth([]);
    }
  };

  useEffect(() => {
    loadProfile();
    loadApplications();
    loadLoanHealth();
  }, []);

  const handleRepay = async (scheduleId) => {
    setRepayError("");
    setRepayingId(scheduleId);
    try {
      await api.post(`/monitoring/repay/${scheduleId}`);
      await loadLoanHealth();
    } catch (err) {
      setRepayError(err.response?.data?.detail || "Could not mark this as repaid.");
    } finally {
      setRepayingId(null);
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setProfileError("");
    setProfileSubmitting(true);
    try {
      await api.post("/business/profile", {
        ...profileForm,
        monthly_income_estimate: Number(profileForm.monthly_income_estimate),
        years_operating: Number(profileForm.years_operating),
      });
      await loadProfile();
    } catch (err) {
      setProfileError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setProfileSubmitting(false);
    }
  };

  const handleApplySubmit = async (e) => {
    e.preventDefault();
    setApplyError("");
    setApplyResult(null);
    setApplySubmitting(true);
    try {
      const res = await api.post("/loans/apply", {
        ...applyForm,
        requested_amount: Number(applyForm.requested_amount),
        term_days: Number(applyForm.term_days),
      });
      setApplyResult(res.data);
      setApplyForm({ requested_amount: "", purpose: "", term_days: "", has_guarantor: false });
      await loadApplications();
    } catch (err) {
      setApplyError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setApplySubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-cream-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-10 space-y-6 sm:space-y-8">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          {profileLoading ? (
            <p className="text-gray-400 text-sm">Loading profile...</p>
          ) : profile ? (
            <div>
              <h2 className="text-lg font-semibold text-indigo-950 mb-3">{profile.business_name}</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                <div>
                  <div className="text-gray-400">Sector</div>
                  <div className="font-medium text-indigo-950">{profile.sector}</div>
                </div>
                <div>
                  <div className="text-gray-400">Monthly income</div>
                  <div className="font-medium text-indigo-950">{profile.monthly_income_estimate}</div>
                </div>
                <div>
                  <div className="text-gray-400">Years operating</div>
                  <div className="font-medium text-indigo-950">{profile.years_operating}</div>
                </div>
              </div>
            </div>
          ) : (
            <div>
              <h2 className="text-lg font-semibold text-indigo-950 mb-1">Create your business profile</h2>
              <p className="text-gray-500 text-sm mb-5">
                You'll need this before applying for a loan.
              </p>
              <form onSubmit={handleProfileSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <input
                  placeholder="Business name"
                  value={profileForm.business_name}
                  onChange={(e) => setProfileForm({ ...profileForm, business_name: e.target.value })}
                  required
                  className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                />
                <input
                  placeholder="Sector (e.g. retail)"
                  value={profileForm.sector}
                  onChange={(e) => setProfileForm({ ...profileForm, sector: e.target.value })}
                  required
                  className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                />
                <input
                  type="number"
                  placeholder="Monthly income estimate"
                  value={profileForm.monthly_income_estimate}
                  onChange={(e) => setProfileForm({ ...profileForm, monthly_income_estimate: e.target.value })}
                  required
                  className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                />
                <input
                  type="number"
                  step="0.1"
                  placeholder="Years operating"
                  value={profileForm.years_operating}
                  onChange={(e) => setProfileForm({ ...profileForm, years_operating: e.target.value })}
                  required
                  className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                />
                {profileError && (
                  <div className="sm:col-span-2 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                    {profileError}
                  </div>
                )}
                <button
                  type="submit"
                  disabled={profileSubmitting}
                  className="sm:col-span-2 bg-indigo-900 hover:bg-indigo-800 text-white font-medium py-2.5 rounded-lg transition disabled:opacity-60"
                >
                  {profileSubmitting ? "Creating..." : "Create profile"}
                </button>
              </form>
            </div>
          )}
        </div>

        {profile && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-5">
              <h2 className="text-lg font-semibold text-indigo-950">Your loan applications</h2>
              <button
                onClick={() => setShowApplyForm(!showApplyForm)}
                className="bg-amber-500 hover:bg-amber-400 text-indigo-950 font-medium px-4 py-2 rounded-lg text-sm transition"
              >
                {showApplyForm ? "Cancel" : "New application"}
              </button>
            </div>

            {showApplyForm && (
              <form onSubmit={handleApplySubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6 pb-6 border-b border-gray-100">
                <input
                  type="number"
                  placeholder="Requested amount"
                  value={applyForm.requested_amount}
                  onChange={(e) => setApplyForm({ ...applyForm, requested_amount: e.target.value })}
                  required
                  className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                />
                <input
                  placeholder="Purpose"
                  value={applyForm.purpose}
                  onChange={(e) => setApplyForm({ ...applyForm, purpose: e.target.value })}
                  required
                  className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                />
                <input
                  type="number"
                  placeholder="Term (days)"
                  value={applyForm.term_days}
                  onChange={(e) => setApplyForm({ ...applyForm, term_days: e.target.value })}
                  required
                  className="px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
                />
                <label className="flex items-center gap-2 text-sm text-gray-600">
                  <input
                    type="checkbox"
                    checked={applyForm.has_guarantor}
                    onChange={(e) => setApplyForm({ ...applyForm, has_guarantor: e.target.checked })}
                    className="rounded"
                  />
                  I have a guarantor
                </label>
                {applyError && (
                  <div className="sm:col-span-2 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                    {applyError}
                  </div>
                )}
                <button
                  type="submit"
                  disabled={applySubmitting}
                  className="sm:col-span-2 bg-indigo-900 hover:bg-indigo-800 text-white font-medium py-2.5 rounded-lg transition disabled:opacity-60"
                >
                  {applySubmitting ? "Submitting..." : "Submit application"}
                </button>
              </form>
            )}

            {applyResult && (
              <div className="mb-6 pb-6 border-b border-gray-100 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-cream-50 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-500">Credit risk</span>
                    <BandBadge band={applyResult.risk_band} />
                  </div>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {applyResult.reasons?.map((r, i) => <li key={i}>• {r}</li>)}
                  </ul>
                </div>
                <div className="bg-cream-50 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-500">Financial stress</span>
                    <BandBadge band={applyResult.stress_band} />
                  </div>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {applyResult.stress_reasons?.map((r, i) => <li key={i}>• {r}</li>)}
                  </ul>
                </div>
              </div>
            )}

            {applications.length === 0 ? (
              <p className="text-gray-400 text-sm">No applications yet.</p>
            ) : (
              <div className="space-y-3">
                {applications.map((app) => (
                  <div
                    key={app.id}
                    className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border border-gray-100 rounded-xl px-4 py-3"
                  >
                    <div>
                      <div className="font-medium text-indigo-950">{app.purpose}</div>
                      <div className="text-sm text-gray-400">
                        {app.requested_amount} over {app.term_days} days · {app.status}
                      </div>
                    </div>
                    <div className="flex gap-2 flex-wrap">
                      <BandBadge band={app.risk_band} />
                      <BandBadge band={app.stress_band} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {profile && loanHealth.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-semibold text-indigo-950 mb-5">Your loan health</h2>

            {repayError && (
              <div className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 mb-4">
                {repayError}
              </div>
            )}

            <div className="space-y-3">
              {loanHealth.map((loan) => (
                <div
                  key={loan.schedule_id}
                  className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border border-gray-100 rounded-xl px-4 py-3"
                >
                  <div>
                    <div className="font-medium text-indigo-950">{loan.purpose}</div>
                    <div className="text-sm text-gray-400">
                      {loan.amount_due} due {new Date(loan.due_date).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <HealthBadge status={loan.health_status} />
                    {!loan.is_paid && (
                      <button
                        onClick={() => handleRepay(loan.schedule_id)}
                        disabled={repayingId === loan.schedule_id}
                        className="bg-indigo-900 hover:bg-indigo-800 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition disabled:opacity-60"
                      >
                        {repayingId === loan.schedule_id ? "Marking..." : "Mark as repaid"}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;