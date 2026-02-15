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