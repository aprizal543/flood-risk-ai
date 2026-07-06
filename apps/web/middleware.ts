import { createServerClient } from "@supabase/ssr";
import { NextRequest, NextResponse } from "next/server";
import { isProtectedPath, isAuthPath } from "@/lib/auth/route-protection";

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
          response = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
        },
      },
    }
  );

  const {
  data: { user },
} = await supabase.auth.getUser();

const pathname = request.nextUrl.pathname;

// Root path — redirect based on authentication state
if (pathname === "/") {
  if (user) return NextResponse.redirect(new URL("/dashboard", request.url));
  return NextResponse.redirect(new URL("/login", request.url));
}

// Protected routes
// Belum login tetapi membuka halaman yang diproteksi
  if (isProtectedPath(pathname) && !user) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Sudah login tetapi membuka login/register
  if (user && isAuthPath(pathname)) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return response;
}

export const config = {
  matcher: [
    "/",
    "/dashboard/:path*",
    "/reports/:path*",
    "/settings/:path*",
    "/login",
    "/register",
  ],
};
