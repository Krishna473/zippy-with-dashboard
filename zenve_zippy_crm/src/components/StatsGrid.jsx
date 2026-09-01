import { useEffect, useState } from "react";
import { fetchStatCounts } from "../api.js";
import { STATS } from "../data.js";


export default function StatsGrid({ refreshTrigger }) {
  const [counts, setCounts] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchStatCounts(STATS).then((result) => {
      if (!cancelled) {
        setCounts(result);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [refreshTrigger]);

  return (
    <div className="zzc-stats-grid">
      {STATS.map((stat) => {
        const value = counts[stat.key];
        return (
          <div className="zzc-stat-card" key={stat.key}>
            <p className="zzc-stat-label">{stat.label}</p>
            <p className="zzc-stat-value">
              {loading ? "…" : value === null ? "—" : value}
            </p>
          </div>
        );
      })}
    </div>
  );
}
