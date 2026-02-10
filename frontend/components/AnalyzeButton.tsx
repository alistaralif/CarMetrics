import { useState, useEffect } from "react";

export default function AnalyzeButton({
  loading,
  onClick,
  onComplete,
}: {
  loading: boolean;
  onClick: () => void;
  onComplete?: () => void;
}) {
  const [progress, setProgress] = useState(0);
  const [showComplete, setShowComplete] = useState(false);

  useEffect(() => {
    if (!loading) {
      if (progress > 0 && !showComplete) {
        // Jump to 100% when loading completes
        setProgress(100);
        setShowComplete(true);
      }
      return;
    }

    setShowComplete(false);

    // Smooth gradual acceleration
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 95) return prev + 0.2;
        return prev + 0.5;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [loading, progress, showComplete]);

  // Handle completion with delay
  useEffect(() => {
    if (showComplete && progress === 100) {
      const timeout = setTimeout(() => {
        if (onComplete) {
          onComplete();
        }
        setProgress(0);
        setShowComplete(false);
      }, 500);
      return () => clearTimeout(timeout);
    }
  }, [showComplete, progress, onComplete]);

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
        {loading || showComplete ? (
          <span className="loading-content">
            <svg
              className="progress-ring"
              width="20"
              height="20"
              viewBox="0 0 20 20"
            >
              {/* Background circle */}
              <circle
                cx="10"
                cy="10"
                r={radius}
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
                opacity="0.2"
              />
              {/* Progress circle */}
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