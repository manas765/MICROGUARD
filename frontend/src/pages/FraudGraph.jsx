import { useEffect, useRef, useState } from "react";
import api from "../lib/api";
import Navbar from "../components/Navbar";

function simulateLayout(nodes, links, width, height, iterations = 300) {
  const positions = {};
  nodes.forEach((n, i) => {
    const angle = (i / nodes.length) * 2 * Math.PI;
    positions[n.id] = {
      x: width / 2 + Math.cos(angle) * 100,
      y: height / 2 + Math.sin(angle) * 100,
      vx: 0,
      vy: 0,
    };
  });

  for (let iter = 0; iter < iterations; iter++) {
    nodes.forEach((a) => {
      let fx = 0, fy = 0;
      nodes.forEach((b) => {
        if (a.id === b.id) return;
        const pa = positions[a.id], pb = positions[b.id];
        const dx = pa.x - pb.x, dy = pa.y - pb.y;
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const repel = 1800 / (dist * dist);
        fx += (dx / dist) * repel;
        fy += (dy / dist) * repel;
      });
      positions[a.id].vx = (positions[a.id].vx + fx) * 0.85;
      positions[a.id].vy = (positions[a.id].vy + fy) * 0.85;
    });

    links.forEach((l) => {
      const pa = positions[l.source], pb = positions[l.target];
      if (!pa || !pb) return;
      const dx = pb.x - pa.x, dy = pb.y - pa.y;
      const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
      const targetDist = 90;
      const pull = (dist - targetDist) * 0.02;
      pa.vx += (dx / dist) * pull;
      pa.vy += (dy / dist) * pull;
      pb.vx -= (dx / dist) * pull;
      pb.vy -= (dy / dist) * pull;
    });

    nodes.forEach((n) => {
      const p = positions[n.id];
      p.x += p.vx;
      p.y += p.vy;
      p.x = Math.max(40, Math.min(width - 40, p.x));
      p.y = Math.max(40, Math.min(height - 40, p.y));
    });
  }

  return positions;
}

const riskColor = (level) => {
  if (level === "high") return "#dc2626";
  if (level === "medium") return "#d97706";
  if (level === "low") return "#2563eb";
  return "#9ca3af";
};

function FraudGraph() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const containerRef = useRef(null);
  const [size, setSize] = useState({ width: 800, height: 500 });

  useEffect(() => {
    const load = async () => {
      setError("");
      setLoading(true);
      try {
        const res = await api.get("/fraud/graph");
        setData(res.data);
      } catch (err) {
        setError(err.response?.data?.detail || "Could not load fraud graph.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (containerRef.current) {
      setSize({ width: containerRef.current.clientWidth, height: 500 });
    }
  }, [data]);

  const positions =
    data && data.nodes.length > 0
      ? simulateLayout(data.nodes, data.links, size.width, size.height)
      : {};

  return (
    <div className="min-h-screen bg-cream-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
        <h1 className="text-lg font-semibold text-indigo-950 mb-2">Fraud ring graph</h1>
        <p className="text-gray-500 text-sm mb-6">
          Applications linked by a shared guarantor phone or signup IP. A cluster of 3 or more is a likely fraud ring.
        </p>

        {error && (
          <div className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-gray-400 text-sm">Loading...</p>
        ) : data && data.nodes.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div className="bg-white rounded-xl border border-gray-100 p-4">
                <div className="text-2xl font-semibold text-indigo-950">{data.nodes.length}</div>
                <div className="text-sm text-gray-400">Linked applications</div>
              </div>
              <div className="bg-white rounded-xl border border-gray-100 p-4">
                <div className="text-2xl font-semibold text-indigo-950">{data.links.length}</div>
                <div className="text-sm text-gray-400">Shared-attribute links</div>
              </div>
              <div className="bg-white rounded-xl border border-gray-100 p-4">
                <div className="text-2xl font-semibold text-red-600">{data.flagged_clusters}</div>
                <div className="text-sm text-gray-400">Flagged clusters (3+)</div>
              </div>
            </div>

            <div
              ref={containerRef}
              className="bg-white rounded-2xl border border-gray-100 p-2 overflow-hidden"
            >
              <svg width={size.width} height={size.height}>
                {data.links.map((l, i) => {
                  const pa = positions[l.source], pb = positions[l.target];
                  if (!pa || !pb) return null;
                  return (
                    <line
                      key={i}
                      x1={pa.x}
                      y1={pa.y}
                      x2={pb.x}
                      y2={pb.y}
                      stroke="#9ca3af"
                      strokeWidth={Math.min(1 + l.weight, 4)}
                      strokeOpacity={0.5}
                    />
                  );
                })}
                {data.nodes.map((n) => {
                  const p = positions[n.id];
                  if (!p) return null;
                  return (
                    <g
                      key={n.id}
                      onClick={() => setSelected(n)}
                      style={{ cursor: "pointer" }}
                    >
                      <circle cx={p.x} cy={p.y} r={10} fill={riskColor(n.fraud_risk_level)} />
                      <text x={p.x} y={p.y - 14} textAnchor="middle" fontSize="10" fill="#4b5563">
                        #{n.id}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            {selected && (
              <div className="mt-4 bg-white rounded-xl border border-gray-100 p-4">
                <div className="font-medium text-indigo-950 mb-1">
                  Application #{selected.id} — {selected.business_name || "Unknown business"}
                </div>
                <div className="text-sm text-gray-500">
                  Requested: {selected.requested_amount} · Status: {selected.status} · Fraud risk:{" "}
                  <span style={{ color: riskColor(selected.fraud_risk_level) }}>
                    {selected.fraud_risk_level || "none"}
                  </span>
                </div>
              </div>
            )}

            <div className="flex gap-4 mt-4 text-xs text-gray-400">
              <span><span className="inline-block w-2 h-2 rounded-full bg-red-600 mr-1" />High</span>
              <span><span className="inline-block w-2 h-2 rounded-full bg-amber-600 mr-1" />Medium</span>
              <span><span className="inline-block w-2 h-2 rounded-full bg-blue-600 mr-1" />Low</span>
              <span><span className="inline-block w-2 h-2 rounded-full bg-gray-400 mr-1" />None</span>
            </div>
          </>
        ) : (
          <p className="text-gray-400 text-sm">No linked applications found — no shared attributes detected.</p>
        )}
      </div>
    </div>
  );
}

export default FraudGraph;