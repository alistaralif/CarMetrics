"use client";

import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { scrapeCars, precacheUrl } from "@/lib/api";
import { useResults } from "@/context/ResultsContext";
import LinkInput from "@/components/LinkInput";
import FinanceCard from "@/components/FinanceCard";
import AnalyzeButton from "@/components/AnalyzeButton";

export default function QuickStart() {
  const [loading, setLoading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const router = useRouter();
  const { setResults, links, setLinks } = useResults();
  
  // Track caching state without re-renders
  const cachingState = useRef({
    cached: new Set<string>(),
    inProgress: new Set<string>(),
    failed: new Set<string>(),
  });

  // Background pre-cache function (no visual updates)
  const precacheLink = useCallback(async (url: string) => {
    const state = cachingState.current;
    
    if (state.cached.has(url) || state.inProgress.has(url)) {
      console.log(`[QuickStart] Skipping precache (already ${state.cached.has(url) ? 'cached' : 'in progress'}):`, url);
      return;
    }

    console.log("[QuickStart] Starting precache for:", url);
    state.inProgress.add(url);

    try {
      const response = await precacheUrl(url);
      console.log("[QuickStart] Precache completed:", url, response);
      
      if (response.cached) {
        console.log("[QuickStart] ✓ Successfully cached:", url);
        state.cached.add(url);
      } else {
        console.warn("[QuickStart] ✗ Failed to cache:", url, response.status);
        state.failed.add(url);
      }
    } catch (error) {
      console.warn("[QuickStart] ✗ Precache error for:", url, error);
      state.failed.add(url);
    } finally {
      state.inProgress.delete(url);
    }
  }, []);

  // Handle new links being added
  const handleLinksChange = useCallback((newLinks: string[]) => {
    const addedLinks = newLinks.filter((link) => !links.includes(link));
    
    if (addedLinks.length > 0) {
      console.log("[QuickStart] New links added:", addedLinks);
    }
    
    setLinks(newLinks);

    // Pre-cache each new link in the background
    addedLinks.forEach((link) => {
      precacheLink(link);
    });
  }, [links, setLinks, precacheLink]);

  async function handleAnalyze() {
    setLoading(true);
    setIsComplete(false);
    
    const state = cachingState.current;
    console.log("[QuickStart] Starting analysis");
    console.log("[QuickStart] Total links:", links.length);
    console.log("[QuickStart] Pre-cached URLs:", [...state.cached]);
    console.log("[QuickStart] Failed precache URLs:", [...state.failed]);

    const startTime = performance.now();

    try {
      const { data, error, requestId, failedUrls, message } = await scrapeCars({
        urls: links,
        userrole: "free",
      });

      const elapsed = Math.round(performance.now() - startTime);
      console.log(`[QuickStart] API response received in ${elapsed}ms:`, { 
        resultCount: data?.length, 
        error, 
        requestId, 
        failedUrls 
      });

      if (error || !data) {
        console.error("[QuickStart] API error:", error);
        alert(error?.message ?? "Unknown error");
        setLoading(false);
        return;
      }

      if (failedUrls && failedUrls.length > 0) {
        console.warn("[QuickStart] Failed URLs:", failedUrls);
        alert(`${message}\n\nFailed links:\n${failedUrls.join("\n")}`);
      }

      console.log("[QuickStart] Setting results:", data.length, "items");
      setResults(data);
      setIsComplete(true);
      setLoading(false);

      setTimeout(() => {
        console.log("[QuickStart] Navigating to /analysis");
        router.push("/analysis");
      }, 500);
    } catch (error) {
      const elapsed = Math.round(performance.now() - startTime);
      console.error(`[QuickStart] Unexpected error after ${elapsed}ms:`, error);
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
          <LinkInput 
            links={links} 
            setLinks={handleLinksChange}
          />
        </div>
      </section>

      <AnalyzeButton
        loading={loading}
        onClick={handleAnalyze}
        isComplete={isComplete}
        linkCount={links.length}
      />
    </main>
  );
}