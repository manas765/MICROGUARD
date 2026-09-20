const COLORS = {
  none: "bg-gray-50 text-gray-400 border-gray-200",
  low: "bg-amber-50 text-amber-600 border-amber-200",
  medium: "bg-orange-50 text-orange-700 border-orange-200",
  high: "bg-red-50 text-red-700 border-red-300",
};

function FraudBadge({ level }) {
  if (!level || level === "none") return null;
  const classes = COLORS[level] || COLORS.medium;
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-medium border border-dashed ${classes}`}>
      Fraud: {level}
    </span>
  );
}

export default FraudBadge;