"use client";

import Hero from "@/components/Hero";
import ResultsTable from "@/components/ResultsTable";
import { sampleCarData } from "@/lib/sampleData";

export default function Home() {
  return (
      <main className="page">
        <Hero />
        <ResultsTable
          data={sampleCarData}
          wrapperClassName="sample"
        />
        {/* <p className="disclaimer-text">
              CarMetrics is an independent analytics tool and is not affiliated with SGCarMart or any vehicle dealer.
              Data is used for informational and analytical purposes only.
        </p> */}
      </main>
  );
}