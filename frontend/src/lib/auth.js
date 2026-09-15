export function saveToken(token) {
  localStorage.setItem("token", token);
}

export function getToken() {
  return localStorage.getItem("token");
}

export function clearToken() {
  localStorage.removeItem("token");
}

export function decodeToken(token) {
  try {
    const payload = token.split(".")[1];
    const decoded = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
    return decoded;
  } catch {
    return null;
  }
}

export function getCurrentUser() {
  const token = getToken();
  if (!token) return null;
  const decoded = decodeToken(token);
  if (!decoded) return null;
  return { id: decoded.sub, role: decoded.role };
}