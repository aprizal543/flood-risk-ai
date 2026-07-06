export function getApiBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_URL;
  if (url) return url.replace(/\/+$/, "");
  if (process.env.NODE_ENV === "production") {
    throw new Error(
      "NEXT_PUBLIC_API_URL is not configured. " +
        "Set it in your Vercel environment variables to the deployed backend URL."
    );
  }
  return "http://localhost:8000";
}
