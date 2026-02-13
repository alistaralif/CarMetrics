import { useState, useEffect } from "react";

export default function AnalyzeButton({
  loading,
  onClick,
  isComplete,
}: {
  loading: boolean;
  onClick: () => void;
  isComplete?: boolean;
}) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!loading) {
      if (isComplete) {
        // Jump to 100% when have results
        setProgress(100);
        const timeout = setTimeout(() => setProgress(0), 500);
        return () => clearTimeout(timeout);
      }
      setProgress(0);
      return;
    }

    // Animate progress while loading (caps at 90%)
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return 90; // Cap at 90% until complete
        return prev + 0.5;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [loading, isComplete]);

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