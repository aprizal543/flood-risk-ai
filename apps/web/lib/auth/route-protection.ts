const PROTECTED_PATHS = [
  "/dashboard",
  "/reports",
  "/settings",
];

const AUTH_PATHS = [
  "/login",
  "/register",
];

export function isProtectedPath(pathname: string): boolean {
  return PROTECTED_PATHS.some((path) =>
    pathname.startsWith(path)
  );
}

export function isAuthPath(pathname: string): boolean {
  return AUTH_PATHS.some((path) =>
    pathname.startsWith(path)
  );
}