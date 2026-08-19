"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { settingsService } from "@/services/settings.service";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Cpu, Check } from "lucide-react";
import { cn } from "@/lib/utils";

export function AIProvidersSection() {
  const { data: providers = [] } = useQuery({
    queryKey: ["ai-providers"],
    queryFn: () => settingsService.getAIProviders(),
  });

  const [selectedDefault, setSelectedDefault] = useState<string>("OpenAI");

  return (
    <Card className="border-border/80 shadow-sm space-y-4">
      <CardHeader>
        <CardTitle className="text-base font-bold">AI Provider Abstraction Layer</CardTitle>
        <CardDescription className="text-xs">
          View connected LLM provider integrations and configure the default execution provider.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {providers.map((p) => {
            const isSelected = selectedDefault === p.name || (selectedDefault === "" && p.is_default);
            return (
              <div
                key={p.name}
                onClick={() => setSelectedDefault(p.name)}
                className={cn(
                  "p-4 rounded-xl border cursor-pointer transition-all flex flex-col justify-between space-y-3",
                  isSelected
                    ? "border-primary bg-primary/5 ring-1 ring-primary"
                    : "border-border/80 bg-card hover:border-primary/50"
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-primary/10 text-primary">
                      <Cpu className="h-4 w-4" />
                    </div>
                    <span className="text-sm font-bold text-foreground">{p.name}</span>
                  </div>
                  {isSelected && (
                    <div className="h-5 w-5 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                      <Check className="h-3 w-3" />
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-muted-foreground font-mono">Model: {p.default_model}</span>
                  <StatusBadge status={p.status} className="text-[10px] py-0" />
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
