import { AuthCardLayout } from "@/components/auth/auth-card-layout";
import { GuestRoute } from "@/components/auth/guest-route";
import { ForgotPasswordForm } from "@/features/auth/forgot-password-form";

export const metadata = {
  title: "Forgot Password — TWIB Platform",
  description: "Reset your TWIB account password.",
};

export default function ForgotPasswordPage() {
  return (
    <GuestRoute>
      <AuthCardLayout
        title="Reset Password"
        subtitle="Enter your email to receive password reset instructions"
      >
        <ForgotPasswordForm />
      </AuthCardLayout>
    </GuestRoute>
  );
}
