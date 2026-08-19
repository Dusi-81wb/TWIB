import { AuthCardLayout } from "@/components/auth/auth-card-layout";
import { GuestRoute } from "@/components/auth/guest-route";
import { ResetPasswordForm } from "@/features/auth/reset-password-form";
import { Suspense } from "react";

export const metadata = {
  title: "Set New Password — TWIB Platform",
  description: "Set a new password for your TWIB account.",
};

export default function ResetPasswordPage() {
  return (
    <GuestRoute>
      <AuthCardLayout
        title="Set New Password"
        subtitle="Enter a new password for your account"
      >
        <Suspense fallback={<div className="text-center text-sm py-4">Loading...</div>}>
          <ResetPasswordForm />
        </Suspense>
      </AuthCardLayout>
    </GuestRoute>
  );
}
