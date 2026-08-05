"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { User as UserIcon, Mail, CheckCircle, Loader2 } from "lucide-react";

export function ProfileSection() {
  const { user } = useAuth();
  const [name, setName] = useState(user?.name || "Samrat Operator");
  const [email] = useState(user?.email || "samrat@twib.ai");
  const [isSaving, setIsSaving] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setIsSuccess(false);
    setTimeout(() => {
      setIsSaving(false);
      setIsSuccess(true);
      setTimeout(() => setIsSuccess(false), 3000);
    }, 1000);
  };

  return (
    <Card className="border-border/80 shadow-sm">
      <CardHeader>
        <CardTitle className="text-base font-bold">Profile Details</CardTitle>
        <CardDescription className="text-xs">
          Manage your personal account profile information and email address.
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSave}>
        <CardContent className="space-y-4">
          {isSuccess && (
            <Alert variant="success" className="border-green-500/50 bg-green-500/10">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <AlertDescription className="text-green-600 dark:text-green-400">
                Profile updated successfully.
              </AlertDescription>
            </Alert>
          )}

          {/* Avatar Preview */}
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-full bg-primary/20 text-primary font-bold flex items-center justify-center text-xl">
              {name.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <p className="text-sm font-semibold text-foreground">{name}</p>
              <p className="text-xs text-muted-foreground">{email}</p>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="profile-name">Full Name</Label>
            <div className="relative">
              <UserIcon className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                id="profile-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="pl-9"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="profile-email">Email Address</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input id="profile-email" value={email} disabled className="pl-9 bg-accent/30 opacity-80" />
            </div>
            <p className="text-[11px] text-muted-foreground">Email changes require organization admin approval.</p>
          </div>
        </CardContent>

        <CardFooter className="pt-2 border-t border-border/60 flex justify-end">
          <Button type="submit" size="sm" disabled={isSaving}>
            {isSaving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...
              </>
            ) : (
              "Save Changes"
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
