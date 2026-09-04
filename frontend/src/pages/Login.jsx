import { useState } from "react";
import axios from "axios";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/login`, {
        email,
        password,
      });
      localStorage.setItem("token", response.data.access_token);
      alert("Login successful!");
    } catch (err) {
      setError("Invalid email or password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-cream-50">
      {/* Left panel - branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-indigo-950 flex-col justify-between p-12 text-white">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-amber-500 flex items-center justify-center font-bold text-indigo-950">
            M
          </div>
          <span className="text-xl font-semibold tracking-tight">MICROGUARD</span>
        </div>

        <div>
          <h1 className="text-4xl font-semibold leading-tight mb-4">
            Smarter lending for small businesses.
          </h1>
          <p className="text-indigo-200 text-lg leading-relaxed max-w-md">
            AI-driven credit scoring, risk simulation, and fraud protection —
            built for microfinance that actually understands its borrowers.
          </p>
        </div>

        <div className="flex gap-8 text-sm text-indigo-300">
          <div>
            <div className="text-2xl font-semibold text-white">500+</div>
            <div>Loans analyzed</div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-white">AI</div>
            <div>Risk scoring</div>
          </div>
          <div>
            <div className="text-2xl font-semibold text-white">24/7</div>
            <div>Monitoring</div>
          </div>
        </div>
      </div>

      {/* Right panel - form */}
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

          <h2 className="text-2xl font-semibold text-indigo-950 mb-2">
            Welcome back
          </h2>
          <p className="text-gray-500 mb-8">
            Log in to manage your loans and business profile.
          </p>

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Email address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition"
              />
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
              {loading ? "Logging in..." : "Log in"}
            </button>
          </form>

          <p className="text-sm text-gray-500 mt-8 text-center">
            Don't have an account?{" "}
            <a href="/signup" className="text-indigo-700 font-medium hover:underline">
             Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;