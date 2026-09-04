import { useState } from "react";
import axios from "axios";

function Signup() {
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "borrower" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await axios.post(`${import.meta.env.VITE_API_URL}/auth/signup`, form);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-cream-50">
      <div className="hidden lg:flex lg:w-1/2 bg-indigo-950 flex-col justify-between p-12 text-white">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-amber-500 flex items-center justify-center font-bold text-indigo-950">
            M
          </div>
          <span className="text-xl font-semibold tracking-tight">MICROGUARD</span>
        </div>

        <div>
          <h1 className="text-4xl font-semibold leading-tight mb-4">
            Get funded, grow with confidence.
          </h1>
          <p className="text-indigo-200 text-lg leading-relaxed max-w-md">
            Create an account to apply for a loan, track your risk score,
            and simulate your business's financial future.
          </p>
        </div>

        <div className="text-sm text-indigo-300">
          Trusted by small businesses across every sector.
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-2 mb-10">
            <div className="w-9 h-9 rounded-lg bg-amber-500 flex items-center justify-center font-bold text-indigo-950">
              M
            </div>
            <span className="text-xl font-semibold tracking-tight text-indigo-950">
              MICROGUARD
            </span>
          </div>

          {success ? (
            <div>
              <h2 className="text-2xl font-semibold text-indigo-950 mb-2">
                Account created
              </h2>
              <p className="text-gray-500 mb-6">
                You can now log in with your new account.
              </p>
              
                 <a             
                href="/"
                className="inline-block bg-indigo-900 hover:bg-indigo-800 text-white font-medium py-2.5 px-6 rounded-lg transition"
              >
                Go to login
              </a>
            </div>
          ) : (
            <>
              <h2 className="text-2xl font-semibold text-indigo-950 mb-2">
                Create your account
              </h2>
              <p className="text-gray-500 mb-8">
                Start your loan application in minutes.
              </p>

              <form onSubmit={handleSignup} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Full name
                  </label>
                  <input
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    placeholder="Jane Doe"
                    required
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Email address
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="you@example.com"
                    required
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Password
                  </label>
                  <input
                    type="password"
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    required
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    I am a
                  </label>
                  <select
                    name="role"
                    value={form.role}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition bg-white"
                  >
                    <option value="borrower">Borrower</option>
                    <option value="loan_officer">Loan officer</option>
                  </select>
                </div>

                {error && (
                  <div className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-indigo-900 hover:bg-indigo-800 text-white font-medium py-2.5 rounded-lg transition disabled:opacity-60"
                >
                  {loading ? "Creating account..." : "Create account"}
                </button>
              </form>

              <p className="text-sm text-gray-500 mt-8 text-center">
                Already have an account?{" "}
                <a href="/" className="text-indigo-700 font-medium hover:underline">
                  Log in
                </a>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Signup;