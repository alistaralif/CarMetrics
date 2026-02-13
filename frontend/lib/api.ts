import { ScrapeRequest, CarListing, ApiError } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function scrapeCars(
  payload: ScrapeRequest
): Promise<{ data?: CarListing[]; error?: ApiError; requestId?: string }> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 min timeout

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

    const data = (await res.json()) as CarListing[];
    return { data, requestId };
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === "AbortError") {
      return { error: { error: "timeout", message: "Request timed out. Try fewer links." } as ApiError };
    }
    throw error;
  }
}