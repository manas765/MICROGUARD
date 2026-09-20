import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const homePath = user?.role === "borrower" ? "/dashboard" : "/officer";

  return (
    <nav className="bg-indigo-950 text-white px-6 py-4 flex items-center justify-between">
      <Link to={homePath} className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center font-bold text-indigo-950 text-sm">
          M
        </div>
        <span className="font-semibold tracking-tight">MICROGUARD</span>
      </Link>

      <div className="flex items-center gap-6 text-sm">
        {user?.role === "borrower" && (
          <>
            <Link to="/dashboard" className="text-indigo-200 hover:text-white transition">
              Dashboard
            </Link>
            <Link to="/forecast" className="text-indigo-200 hover:text-white transition">
              Forecast
            </Link>
          </>
        )}
        {(user?.role === "loan_officer" || user?.role === "admin") && (
          <>
            <Link to="/officer" className="text-indigo-200 hover:text-white transition">
              Applications
            </Link>
            <Link to="/monitoring" className="text-indigo-200 hover:text-white transition">
              Monitoring
            </Link>
          </>
        )}
        <button onClick={handleLogout} className="text-indigo-200 hover:text-white transition">
          Log out
        </button>
      </div>
    </nav>
  );
}

export default Navbar;