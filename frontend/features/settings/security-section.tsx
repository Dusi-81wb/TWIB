"use client";

import { useState } from "react";
import { settingsService } from "@/services/settings.service";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Lock, LogOut, CheckCircle, Loader2, ShieldCheck } from "lucide-react";

export function SecuritySection() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setIsSuccess(false);

    if (newPassword !== confirmPassword) {
      setErrorMsg("New passwords do not match.");
      return;
    }

    if (newPassword.length < 8) {
      setErrorMsg("New password must be at least 8 characters.");
      return;
    }

    setIsSubmitting(true);
    try {
      await settingsService.changePassword(oldPassword, newPassword);
      setIsSuccess(true);
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch {
      setErrorMsg("Failed to update password. Verify your current password.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Change Password */}
      <Card className="border-border/80 shadow-sm">
        <CardHeader>
          <CardTitle className="text-base font-bold">Security & Password</CardTitle>
          <CardDescription className="text-xs">
            Update your account password and security authorization preferences.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleChangePassword}>
          <CardContent className="space-y-4">
            {isSuccess && (
              <Alert variant="success" className="border-green-500/50 bg-green-500/10">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <AlertDescription className="text-green-600 dark:text-green-400">
                  Password updated successfully.
                </AlertDescription>
              </Alert>
            )}

            {errorMsg && (
              <Alert variant="destructive">
                <AlertDescription>{errorMsg}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="old-password">Current Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="old-password"
                  type="password"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  className="pl-9"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="new-password">New Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="new-password"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="pl-9"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm-password">Confirm New Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="pl-9"
                  required
                />
              </div>
            </div>
          </CardContent>

          <CardFooter className="pt-2 border-t border-border/60 flex justify-end">
            <Button type="submit" size="sm" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Updating...
                </>
              ) : (
                "Update Password"
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>

      {/* Active Sessions */}
      <Card className="border-border/80 shadow-sm">
        <CardHeader>
          <CardTitle className="text-base font-bold">Active Sessions</CardTitle>
          <CardDescription className="text-xs">
            Manage logged-in devices and active JWT authorization sessions.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded-xl border border-border/60 bg-accent/20 text-xs">
            <div className="flex items-center gap-3">
              <ShieldCheck className="h-4 w-4 text-green-500" />
              <div>
                <p className="font-semibold text-foreground">Current Web Browser Session</p>
                <p className="text-[11px] text-muted-foreground">Chrome on Windows &bull; Active Now</p>
              </div>
            </div>
            <Button variant="outline" size="sm" className="text-xs text-destructive">
              <LogOut className="h-3.5 w-3.5 mr-1" /> Logout All Sessions
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
