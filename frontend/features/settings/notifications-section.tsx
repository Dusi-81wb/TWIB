"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Bell, CheckCircle2, AlertTriangle, ShieldAlert } from "lucide-react";

export function NotificationsSection() {
  const [toggles, setToggles] = useState({
    completed: true,
    failed: true,
    approval: true,
    systemAlerts: false,
  });

  const handleToggle = (key: keyof typeof toggles) => {
    setToggles((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <Card className="border-border/80 shadow-sm space-y-4">
      <CardHeader>
        <CardTitle className="text-base font-bold">Notification & Alert Settings</CardTitle>
        <CardDescription className="text-xs">
          Configure telemetry alert preferences and real-time push notifications.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between p-3.5 rounded-xl border border-border/60 bg-accent/20">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="h-4 w-4 text-green-500" />
            <div className="space-y-0.5">
              <Label htmlFor="toggle-completed" className="text-xs font-bold cursor-pointer">
                Workflow Completed Alerts
              </Label>
              <p className="text-[11px] text-muted-foreground">Receive notification when a workflow finishes cleanly.</p>
            </div>
          </div>
          <input
            type="checkbox"
            id="toggle-completed"
            checked={toggles.completed}
            onChange={() => handleToggle("completed")}
            className="h-4 w-4 rounded border-input bg-background text-primary focus:ring-ring cursor-pointer"
          />
        </div>

        <div className="flex items-center justify-between p-3.5 rounded-xl border border-border/60 bg-accent/20">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-4 w-4 text-red-500" />
            <div className="space-y-0.5">
              <Label htmlFor="toggle-failed" className="text-xs font-bold cursor-pointer">
                Workflow Failure Alerts
              </Label>
              <p className="text-[11px] text-muted-foreground">Receive instant alert when an agent step fails.</p>
            </div>
          </div>
          <input
            type="checkbox"
            id="toggle-failed"
            checked={toggles.failed}
            onChange={() => handleToggle("failed")}
            className="h-4 w-4 rounded border-input bg-background text-primary focus:ring-ring cursor-pointer"
          />
        </div>

        <div className="flex items-center justify-between p-3.5 rounded-xl border border-border/60 bg-accent/20">
          <div className="flex items-center gap-3">
            <ShieldAlert className="h-4 w-4 text-amber-500" />
            <div className="space-y-0.5">
              <Label htmlFor="toggle-approval" className="text-xs font-bold cursor-pointer">
                Human Checkpoint Sign-Off Required
              </Label>
              <p className="text-[11px] text-muted-foreground">Alert when workflow reaches human sign-off checkpoint.</p>
            </div>
          </div>
          <input
            type="checkbox"
            id="toggle-approval"
            checked={toggles.approval}
            onChange={() => handleToggle("approval")}
            className="h-4 w-4 rounded border-input bg-background text-primary focus:ring-ring cursor-pointer"
          />
        </div>

        <div className="flex items-center justify-between p-3.5 rounded-xl border border-border/60 bg-accent/20">
          <div className="flex items-center gap-3">
            <Bell className="h-4 w-4 text-primary" />
            <div className="space-y-0.5">
              <Label htmlFor="toggle-alerts" className="text-xs font-bold cursor-pointer">
                Subsystem System Health Alerts
              </Label>
              <p className="text-[11px] text-muted-foreground">Notify on database, cache or LLM provider status changes.</p>
            </div>
          </div>
          <input
            type="checkbox"
            id="toggle-alerts"
            checked={toggles.systemAlerts}
            onChange={() => handleToggle("systemAlerts")}
            className="h-4 w-4 rounded border-input bg-background text-primary focus:ring-ring cursor-pointer"
          />
        </div>
      </CardContent>
    </Card>
  );
}
