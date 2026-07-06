import { createServerClient } from "@supabase/ssr";
import { NextRequest, NextResponse } from "next/server";

function getErrorRedirect(request: NextRequest, message: string) {
  return NextResponse.redirect(new URL(`/login?oauth_error=${encodeURIComponent(message)}`, request.url));
}

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const error = request.nextUrl.searchParams.get("error");
  const errorDescription = request.nextUrl.searchParams.get("error_description");

  if (error || !code) {
    return getErrorRedirect(request, errorDescription ?? "Google sign-in gagal.");
  }

  const response = NextResponse.redirect(new URL("/dashboard", request.url));

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            response.cookies.set(name, value, options);
          });
        },
      },
    }
  );

  const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);

  if (exchangeError) {
    return getErrorRedirect(request, exchangeError.message);
  }

  return response;
}