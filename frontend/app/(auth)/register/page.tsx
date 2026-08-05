import { AuthCardLayout } from "@/components/auth/auth-card-layout";
import { GuestRoute } from "@/components/auth/guest-route";
import { RegisterForm } from "@/features/auth/register-form";

export const metadata = {
  title: "Create Account — TWIB Platform",
  description: "Get started with TWIB enterprise AI workflow orchestration.",
};

export default function RegisterPage() {
  return (
    <GuestRoute>
      <AuthCardLayout
        title="Create your account"
        subtitle="Start building autonomous multi-agent workflows"
      >
        <RegisterForm />
      </AuthCardLayout>
    </GuestRoute>
  );
}
