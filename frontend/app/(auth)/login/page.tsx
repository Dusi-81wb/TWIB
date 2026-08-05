import { AuthCardLayout } from "@/components/auth/auth-card-layout";
import { GuestRoute } from "@/components/auth/guest-route";
import { LoginForm } from "@/features/auth/login-form";

export const metadata = {
  title: "Sign In — TWIB Platform",
  description: "Sign in to your TWIB account to manage AI workflows.",
};

export default function LoginPage() {
  return (
    <GuestRoute>
      <AuthCardLayout
        title="Welcome Back"
        subtitle="Sign in to access your intelligence workflows"
      >
        <LoginForm />
      </AuthCardLayout>
    </GuestRoute>
  );
}
