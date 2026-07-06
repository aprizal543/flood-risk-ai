import { AuthShell } from "@/components/auth/AuthShell";
import { LoginCard } from "@/components/auth/LoginCard";

export function AuthLayout() {
  return (
    <AuthShell>
      <LoginCard />
    </AuthShell>
  );
}
