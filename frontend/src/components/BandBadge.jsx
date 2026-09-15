const COLORS = {
  Low: "bg-green-100 text-green-700",
  Medium: "bg-amber-100 text-amber-700",
  High: "bg-red-100 text-red-700",
};

function BandBadge({ band }) {
  if (!band) return <span className="text-gray-400 text-sm">—</span>;
  const classes = COLORS[band] || "bg-gray-100 text-gray-700";
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${classes}`}>
      {band}
    </span>
  );
}

export default BandBadge;