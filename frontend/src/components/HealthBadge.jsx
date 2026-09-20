const COLORS = {
  overdue: "bg-red-100 text-red-700",
  due_soon: "bg-amber-100 text-amber-700",
  on_track: "bg-green-100 text-green-700",
  paid_on_time: "bg-green-100 text-green-700",
  paid_late: "bg-amber-100 text-amber-700",
};

const LABELS = {
  overdue: "Overdue",
  due_soon: "Due soon",
  on_track: "On track",
  paid_on_time: "Paid on time",
  paid_late: "Paid late",
};

function HealthBadge({ status }) {
  if (!status) return <span className="text-gray-400 text-sm">—</span>;
  const classes = COLORS[status] || "bg-gray-100 text-gray-700";
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${classes}`}>
      {LABELS[status] || status}
    </span>
  );
}

export default HealthBadge;