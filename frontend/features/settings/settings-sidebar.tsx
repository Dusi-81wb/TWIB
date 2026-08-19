import { User, Shield, Palette, Bell, Cpu, Key, Lock, Info } from "lucide-react";
import { cn } from "@/lib/utils";

export type SettingsTab =
  | "profile"
  | "account"
  | "appearance"
  | "notifications"
  | "providers"
  | "apikeys"
  | "security"
  | "about";

interface SettingsSidebarProps {
  activeTab: SettingsTab;
  onTabChange: (tab: SettingsTab) => void;
}

const tabs: { id: SettingsTab; label: string; icon: typeof User }[] = [
  { id: "profile", label: "Profile", icon: User },
  { id: "account", label: "Account", icon: Shield },
  { id: "appearance", label: "Appearance", icon: Palette },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "providers", label: "AI Providers", icon: Cpu },
  { id: "apikeys", label: "API Keys", icon: Key },
  { id: "security", label: "Security", icon: Lock },
  { id: "about", label: "About", icon: Info },
];

export function SettingsSidebar({ activeTab, onTabChange }: SettingsSidebarProps) {
  return (
    <nav className="space-y-1 w-full md:w-56 flex-shrink-0">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-xs font-semibold transition-colors text-left",
              isActive
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:bg-accent hover:text-foreground"
            )}
          >
            <Icon className="h-4 w-4 flex-shrink-0" />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
