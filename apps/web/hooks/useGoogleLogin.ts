"use client";

import { useCallback, useState } from "react";
import { signInWithGoogle } from "@/lib/auth/google";

export function useGoogleLogin() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startGoogleLogin = useCallback(async () => {
    if (loading) {
      return;
    }

    setError(null);
    setLoading(true);

    const { error: signInError } = await signInWithGoogle();
    if (signInError) {
      setError(signInError.message);
      setLoading(false);
    }
  }, [loading]);

  return { startGoogleLogin, loading, error };
}
