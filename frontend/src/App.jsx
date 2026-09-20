import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Forecast from "./pages/Forecast";
import OfficerDashboard from "./pages/OfficerDashboard";
import Monitoring from "./pages/Monitoring";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute allowedRoles={["borrower"]}>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/forecast"
            element={
              <ProtectedRoute allowedRoles={["borrower"]}>
                <Forecast />
              </ProtectedRoute>
            }
          />
          <Route
            path="/officer"
            element={
              <ProtectedRoute allowedRoles={["loan_officer", "admin"]}>
                <OfficerDashboard />
              </ProtectedRoute>
            }
          />
                    <Route
            path="/officer"
            element={
              <ProtectedRoute allowedRoles={["loan_officer", "admin"]}>
                <OfficerDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/monitoring"
            element={
              <ProtectedRoute allowedRoles={["loan_officer", "admin"]}>
                <Monitoring />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;