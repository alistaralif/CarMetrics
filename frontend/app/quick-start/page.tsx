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
  const router = useRouter();
  const { setResults, links, setLinks } = useResults();

  async function handleAnalyze() {
    setLoading(true);

    try {
      const { data, error } = await scrapeCars({
        urls: links,
        userrole: "free",
      });

      if (error || !data) {
        alert(error?.message ?? "Unknown error");
        return;
      }

      setResults(data);
    } catch (error) {
      console.error(error);
    }

    setLoading(false);
  }

  const handleComplete = () => {
    router.push("/analysis");
  };

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
        onComplete={handleComplete}
      />
    </main>
  );
}