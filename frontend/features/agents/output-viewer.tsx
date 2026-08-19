import { StatusBadge } from "@/components/dashboard/status-badge";
import { Card } from "@/components/ui/card";
import { Clock, ShieldCheck, Terminal, Copy, Check } from "lucide-react";
import { useState } from "react";
import { AgentExecuteResponse } from "@/services/agent.service";

interface OutputViewerProps {
  response: AgentExecuteResponse | null;
  error?: string | null;
}

export function OutputViewer({ response, error }: OutputViewerProps) {
  const [copied, setCopied] = useState(false);

  if (error) {
    return (
      <Card className="p-4 border-red-500/50 bg-red-500/5 text-xs text-red-500 space-y-1">
        <p className="font-bold">Agent Execution Failed</p>
        <p className="font-mono">{error}</p>
      </Card>
    );
  }

  if (!response) {
    return (
      <Card className="p-8 border-border/80 bg-card text-center text-xs text-muted-foreground space-y-2">
        <Terminal className="h-8 w-8 mx-auto text-muted-foreground/40" />
        <p className="font-medium text-foreground">Agent Output Console</p>
        <p className="text-[11px]">Select an agent, enter prompt instructions, and click Execute Agent.</p>
      </Card>
    );
  }

  const rawOutput =
    typeof response.output === "string"
      ? response.output
      : JSON.stringify(response.output, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(rawOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className="p-5 border-border/80 bg-card space-y-4">
      {/* Header Info */}
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <div className="flex items-center gap-3">
          <StatusBadge status={response.status} />
          <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono">
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" /> {response.duration_seconds}s
            </span>
            {response.confidence !== undefined && (
              <span className="flex items-center gap-1 text-green-500">
                <ShieldCheck className="h-3.5 w-3.5" /> {(response.confidence * 100).toFixed(0)}% Confidence
              </span>
            )}
          </div>
        </div>

        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
          <span>{copied ? "Copied" : "Copy Output"}</span>
        </button>
      </div>

      {/* Output Content */}
      <div className="space-y-1">
        <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider block">
          Response Output
        </span>
        <pre className="p-4 rounded-xl bg-accent/30 border border-border/50 text-xs font-mono text-foreground overflow-x-auto whitespace-pre-wrap max-h-96">
          {rawOutput}
        </pre>
      </div>
    </Card>
  );
}
