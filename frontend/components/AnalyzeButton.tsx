import { useState, useEffect } from "react";

export default function AnalyzeButton({
  loading,
  onClick,
  isComplete,
  linkCount = 1,
}: {
  loading: boolean;
  onClick: () => void;
  isComplete?: boolean;
  linkCount?: number;
}) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!loading) {
      if (isComplete) {
        setProgress(100);
        const timeout = setTimeout(() => setProgress(0), 500);
        return () => clearTimeout(timeout);
      }
      setProgress(0);
      return;
    }

    // Calculate increment based on expected time
    // Assume ~5-10 seconds per link, cap at 90% over that time
    const estimatedTimeMs = Math.max(linkCount * 7000, 10000); // min 10 seconds
    const targetProgress = 90;
    const updateIntervalMs = 200;
    const totalUpdates = estimatedTimeMs / updateIntervalMs;
    const incrementPerUpdate = targetProgress / totalUpdates;

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return 90;
        return Math.min(prev + incrementPerUpdate, 90);
      });
    }, updateIntervalMs);

    return () => clearInterval(interval);
  }, [loading, isComplete, linkCount]);

// Circle progress calculation
  const radius = 8;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="analyze-wrapper">
      <button
        className="analyze-btn"
        onClick={onClick}
        disabled={loading}
      >
        {loading ? (
          <span className="loading-content">
            <svg
              className="progress-ring"
              width="20"
              height="20"
              viewBox="0 0 20 20"
            >
              <circle
                cx="10"
                cy="10"
                r={radius}
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
                opacity="0.2"
              />
              <circle
                cx="10"
                cy="10"
                r={radius}
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                transform="rotate(-90 10 10)"
              />
            </svg>
            <span>Analysing…</span>
          </span>
        ) : (
          "Analyse"
        )}
      </button>
    </div>
  );
}