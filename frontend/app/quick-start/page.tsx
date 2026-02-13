"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { scrapeCars } from "@/lib/api";
import { useResults } from "@/context/ResultsContext";
import LinkInput from "@/components/LinkInput";
import FinanceCard from "@/components/FinanceCard";
import AnalyzeButton from "@/components/AnalyzeButton";

export default function QuickStart() {
  const [loading, setLoading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const router = useRouter();
  const { setResults, links, setLinks } = useResults();

  async function handleAnalyze() {
    setLoading(true);
    setIsComplete(false);
    console.log("[QuickStart] Starting analysis with links:", links);

    try {
      const { data, error, requestId } = await scrapeCars({
        urls: links,
        userrole: "free",
      });

      console.log("[QuickStart] API response received:", { data, error, requestId });

      if (error || !data) {
        console.error("[QuickStart] API error:", error);
        alert(error?.message ?? "Unknown error");
        setLoading(false);
        return;
      }

      console.log("[QuickStart] Setting results:", data.length, "items");
      setResults(data);
      setIsComplete(true);
      setLoading(false);

      // Navigate after a short delay to show completion
      setTimeout(() => {
        console.log("[QuickStart] Navigating to /analysis");
        router.push("/analysis");
      }, 500);
    } catch (error) {
      console.error("[QuickStart] Unexpected error:", error);
      alert("An unexpected error occurred");
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <h1 className="quickstart-header">Quick Start</h1>

      <section className="quickstart-grid">
        <FinanceCard />
        <div className="card">
          <LinkInput links={links} setLinks={setLinks} />
        </div>
      </section>

      <AnalyzeButton
        loading={loading}
        onClick={handleAnalyze}
        isComplete={isComplete}
      />
    </main>
  );
}