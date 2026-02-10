import { ScrapeRequest, CarListing, ApiError } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function scrapeCars(
  payload: ScrapeRequest
): Promise<{ data?: CarListing[]; error?: ApiError; requestId?: string }> {
  const res = await fetch(`${API_BASE}/api/scrape`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const requestId = res.headers.get("X-Request-ID") ?? undefined;

  if (!res.ok) {
    const err = (await res.json()) as ApiError;
    return { error: err, requestId };
  }

  const data = (await res.json()) as CarListing[];
  return { data, requestId };
}