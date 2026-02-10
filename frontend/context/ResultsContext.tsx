"use client";

import { createContext, useContext, useState } from "react";
import type { CarListing } from "@/lib/types";

type ResultsContextType = {
  results: CarListing[];
  setResults: (r: CarListing[]) => void;
  appendResults: (r: CarListing[]) => void;
  clearResults: () => void;
  links: string[];
  setLinks: (l: string[]) => void;
};

const ResultsContext = createContext<ResultsContextType | null>(null);

export function ResultsProvider({ children }: { children: React.ReactNode }) {
  const [results, setResults] = useState<CarListing[]>([]);
  const [links, setLinks] = useState<string[]>([]);

  const appendResults = (newResults: CarListing[]) => {
    setResults((prev) => [...prev, ...newResults]);
  };

  const clearResults = () => {
    setResults([]);
  };

  return (
    <ResultsContext.Provider value={{ results, setResults, appendResults, clearResults, links, setLinks }}>
      {children}
    </ResultsContext.Provider>
  );
}

export function useResults() {
  const ctx = useContext(ResultsContext);
  if (!ctx) throw new Error("useResults must be used inside ResultsProvider");
  return ctx;
}