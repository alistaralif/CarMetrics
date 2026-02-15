import { ScrapeRequest, CarListing, ApiError, ScrapeResponse } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function scrapeCars(
  payload: ScrapeRequest
): Promise<{ data?: CarListing[]; error?: ApiError; requestId?: string; failedUrls?: string[]; message?: string }> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 120000);

  try {
    const res = await fetch(`${API_BASE}/api/scrape`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const requestId = res.headers.get("X-Request-ID") ?? undefined;

    if (!res.ok) {
      const err = (await res.json()) as ApiError;
      return { error: err, requestId };
    }

    const response = (await res.json()) as ScrapeResponse;
    return { 
      data: response.results, 
      requestId,
      failedUrls: response.failed_urls,
      message: response.message
    };
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === "AbortError") {
      return { error: { error: "timeout", message: "Request timed out. Try fewer links." } as ApiError };
    }
    throw error;
  }
}

interface PrecacheResponse {
  status: string;
  url: string;
  cached: boolean;
}

/**
 * Pre-cache a single URL in the background.
 * This triggers scraping and caching but doesn't return analysis data.
 */
export async function precacheUrl(url: string): Promise<PrecacheResponse> {
  const startTime = performance.now();
  console.log(`[API] Precache request started for: ${url}`);
  
  try {
    const res = await fetch(`${API_BASE}/api/precache`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });

    const elapsed = Math.round(performance.now() - startTime);

    if (!res.ok) {
      const errorText = await res.text();
      console.error(`[API] Precache failed (${res.status}) after ${elapsed}ms:`, errorText);
      throw new Error(`Precache failed: ${res.statusText}`);
    }

    const data = await res.json() as PrecacheResponse;
    console.log(`[API] Precache response (${elapsed}ms):`, data);
    
    return data;
  } catch (error) {
    const elapsed = Math.round(performance.now() - startTime);
    console.error(`[API] Precache error after ${elapsed}ms:`, error);
    throw error;
  }
}