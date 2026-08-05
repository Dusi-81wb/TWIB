"use client";

import { useQuery } from "@tanstack/react-query";
import { workflowService, WorkflowTemplateItem } from "@/services/workflow.service";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { FileCode, Sparkles, Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface TemplateSelectorProps {
  selectedTemplateId: string;
  onSelectTemplate: (template: WorkflowTemplateItem | null) => void;
}

const fallbackTemplates: WorkflowTemplateItem[] = [
  {
    id: "software_architecture",
    name: "Software Architecture Audit",
    category: "engineering",
    description: "Evaluates system architecture, designs microservices, and validates security.",
    suggested_prompt: "Design a scalable enterprise ERP microservices architecture.",
  },
  {
    id: "market_research",
    name: "Autonomous Market Research",
    category: "strategy",
    description: "Gathers intelligence, analyzes competitors, and computes market sizing.",
    suggested_prompt: "Analyze the global generative AI market opportunity for 2026.",
  },
  {
    id: "security_audit",
    name: "Multi-Agent Security Audit",
    category: "compliance",
    description: "Scans codebase, evaluates OWASP vulnerabilities, and drafts compliance docs.",
    suggested_prompt: "Perform a comprehensive security audit of an OAuth2 authentication API.",
  },
];

export function TemplateSelector({ selectedTemplateId, onSelectTemplate }: TemplateSelectorProps) {
  const { data: templates, isLoading } = useQuery({
    queryKey: ["workflow-templates"],
    queryFn: () => workflowService.getTemplates(),
  });

  const activeTemplates = templates && templates.length > 0 ? templates : fallbackTemplates;

  return (
    <div className="space-y-3">
      <Label className="text-sm font-semibold">Select Workflow Blueprint Template</Label>
      <p className="text-xs text-muted-foreground">
        Choose a pre-configured template or build a custom workflow from scratch.
      </p>

      {isLoading ? (
        <div className="flex items-center justify-center p-6 border border-border rounded-xl">
          <Loader2 className="h-5 w-5 animate-spin text-primary mr-2" />
          <span className="text-xs text-muted-foreground">Loading templates...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {/* Custom No Template Option */}
          <Card
            onClick={() => onSelectTemplate(null)}
            className={cn(
              "p-4 cursor-pointer transition-all border hover:border-primary/50 relative flex flex-col justify-between",
              selectedTemplateId === "none" || !selectedTemplateId
                ? "border-primary bg-primary/5 ring-1 ring-primary"
                : "border-border/80 bg-card"
            )}
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="p-2 rounded-lg bg-secondary text-foreground">
                  <Sparkles className="h-4 w-4" />
                </div>
                {(selectedTemplateId === "none" || !selectedTemplateId) && (
                  <div className="h-5 w-5 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                    <Check className="h-3 w-3" />
                  </div>
                )}
              </div>
              <h4 className="text-xs font-bold text-foreground">Custom Workflow</h4>
              <p className="text-[11px] text-muted-foreground line-clamp-2">
                Start from scratch with custom parameters and default multi-agent pipeline.
              </p>
            </div>
          </Card>

          {/* Template Items */}
          {activeTemplates.map((template) => {
            const isSelected = selectedTemplateId === template.id;
            return (
              <Card
                key={template.id}
                onClick={() => onSelectTemplate(template)}
                className={cn(
                  "p-4 cursor-pointer transition-all border hover:border-primary/50 relative flex flex-col justify-between",
                  isSelected ? "border-primary bg-primary/5 ring-1 ring-primary" : "border-border/80 bg-card"
                )}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="p-2 rounded-lg bg-primary/10 text-primary">
                      <FileCode className="h-4 w-4" />
                    </div>
                    {isSelected && (
                      <div className="h-5 w-5 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                        <Check className="h-3 w-3" />
                      </div>
                    )}
                  </div>
                  <h4 className="text-xs font-bold text-foreground">{template.name}</h4>
                  <p className="text-[11px] text-muted-foreground line-clamp-2">{template.description}</p>
                </div>
                <span className="inline-block mt-3 text-[10px] font-medium uppercase tracking-wider text-primary">
                  {template.category}
                </span>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
