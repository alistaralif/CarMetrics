"use client";

import { useResults } from "@/context/ResultsContext";
import ResultsTable from "@/components/ResultsTable";
import { HiOutlineSaveAs } from "react-icons/hi";
import { VscDebugRestart } from "react-icons/vsc";
import type { CarListing } from "@/lib/types";

export default function Analysis() {
  const { results, clearResults } = useResults();

  const handleSaveAsCSV = () => {
    if (!results || results.length === 0) {
      console.warn("No data to export");
      return;
    }

    try {
      // Get column headers from the first result object
      const headers = Object.keys(results[0]) as (keyof CarListing)[];
      
      // Create CSV header row
      const csvHeader = headers.join(",");
      
      // Create CSV data rows
      const csvRows = results.map((item) =>
        headers
          .map((header) => {
            const value = item[header];
            // Handle arrays, nulls, and escape commas/quotes
            if (Array.isArray(value)) {
              return `"${value.join("; ")}"`;
            }
            if (value === null || value === undefined) {
              return "";
            }
            const stringValue = String(value);
            // Escape quotes and wrap in quotes if contains comma
            if (stringValue.includes(",") || stringValue.includes('"')) {
              return `"${stringValue.replace(/"/g, '""')}"`;
            }
            return stringValue;
          })
          .join(",")
      );

      // Combine header and rows
      const csvContent = [csvHeader, ...csvRows].join("\n");

      // Create and download file
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "carmetrics.csv";
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("CSV export failed:", error);
    }
  };

  const handleClearResults = () => {
    clearResults();
  };

  return (
      <main className="page">
      <div className="analysis-header-container">
          <h1 className="analysis-header">Analysis</h1>
          <div className="analysis-actions">
            <button 
              onClick={handleClearResults} 
              className="clear-results-btn" 
              title="Clear Results"
              disabled={results.length === 0}
            >
              <VscDebugRestart size={24} />
            </button>
            <button 
              onClick={handleSaveAsCSV} 
              className="save-csv-btn" 
              title="Save as CSV"
              disabled={results.length === 0}
            >
              <HiOutlineSaveAs size={24} />
            </button>
          </div>
      </div>
      <div>
        <ResultsTable data={results} wrapperClassName="results" />
      </div>
    </main>
  );
}
