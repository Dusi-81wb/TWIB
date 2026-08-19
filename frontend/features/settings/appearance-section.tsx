"use client";

import { useTheme } from "@/hooks/use-theme";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Sun, Moon, Laptop, Check } from "lucide-react";
import { cn } from "@/lib/utils";

export function AppearanceSection() {
  const { theme, setTheme } = useTheme();

  return (
    <Card className="border-border/80 shadow-sm space-y-4">
      <CardHeader>
        <CardTitle className="text-base font-bold">Appearance & Theme Preferences</CardTitle>
        <CardDescription className="text-xs">
          Customize the visual theme of the TWIB Platform interface.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Light Mode */}
          <div
            onClick={() => setTheme("light")}
            className={cn(
              "p-4 rounded-2xl border cursor-pointer transition-all flex flex-col justify-between space-y-3",
              theme === "light"
                ? "border-primary bg-primary/5 ring-1 ring-primary"
                : "border-border/80 bg-card hover:border-primary/50"
            )}
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-amber-500/10 text-amber-500">
                <Sun className="h-5 w-5" />
              </div>
              {theme === "light" && (
                <div className="h-5 w-5 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                  <Check className="h-3 w-3" />
                </div>
              )}
            </div>
            <div>
              <p className="text-sm font-bold text-foreground">Light Theme</p>
              <p className="text-xs text-muted-foreground">High contrast light background</p>
            </div>
          </div>

          {/* Dark Mode */}
          <div
            onClick={() => setTheme("dark")}
            className={cn(
              "p-4 rounded-2xl border cursor-pointer transition-all flex flex-col justify-between space-y-3",
              theme === "dark"
                ? "border-primary bg-primary/5 ring-1 ring-primary"
                : "border-border/80 bg-card hover:border-primary/50"
            )}
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                <Moon className="h-5 w-5" />
              </div>
              {theme === "dark" && (
                <div className="h-5 w-5 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                  <Check className="h-3 w-3" />
                </div>
              )}
            </div>
            <div>
              <p className="text-sm font-bold text-foreground">Dark Theme</p>
              <p className="text-xs text-muted-foreground">Sleek dark mode interface</p>
            </div>
          </div>

          {/* System Default */}
          <div
            onClick={() => setTheme("system")}
            className={cn(
              "p-4 rounded-2xl border cursor-pointer transition-all flex flex-col justify-between space-y-3",
              theme === "system"
                ? "border-primary bg-primary/5 ring-1 ring-primary"
                : "border-border/80 bg-card hover:border-primary/50"
            )}
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-secondary text-foreground">
                <Laptop className="h-5 w-5" />
              </div>
              {theme === "system" && (
                <div className="h-5 w-5 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                  <Check className="h-3 w-3" />
                </div>
              )}
            </div>
            <div>
              <p className="text-sm font-bold text-foreground">System Preference</p>
              <p className="text-xs text-muted-foreground">Sync with OS color theme</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
