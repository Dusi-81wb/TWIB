import type { ReactNode } from "react";
import { ThemeToggle } from "@/components/theme-toggle";
import { Card } from "@/components/ui/card";
import { Layers } from "lucide-react";
import Link from "next/link";

interface AuthCardLayoutProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

export function AuthCardLayout({ children, title, subtitle }: AuthCardLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-4 bg-background relative overflow-hidden">
      {/* Top Header Controls */}
      <header className="absolute top-4 right-4 flex items-center gap-2">
        <ThemeToggle />
      </header>

      {/* Main Container */}
      <div className="w-full max-w-md space-y-6">
        {/* Brand / Logo */}
        <div className="flex flex-col items-center text-center space-y-2">
          <Link href="/" className="flex items-center gap-2 font-bold text-2xl tracking-tight">
            <div className="p-2 rounded-xl bg-primary text-primary-foreground shadow-md">
              <Layers className="h-6 w-6" />
            </div>
            <span>TWIB</span>
          </Link>
          <h1 className="text-xl font-semibold text-foreground tracking-tight">{title}</h1>
          {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
        </div>

        {/* Form Card */}
        <Card className="p-6 border-border shadow-xl backdrop-blur-sm bg-card/95">
          {children}
        </Card>

        {/* Footer info */}
        <footer className="text-center text-xs text-muted-foreground">
          TWIB Platform &copy; {new Date().getFullYear()} — Total Workflow Intelligence Builder
        </footer>
      </div>
    </div>
  );
}
