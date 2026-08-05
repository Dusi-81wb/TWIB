"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Play, RotateCcw, Loader2, Sparkles } from "lucide-react";

interface PromptEditorProps {
  onExecute: (prompt: string) => void;
  isExecuting: boolean;
  defaultPrompt?: string;
}

export function PromptEditor({
  onExecute,
  isExecuting,
  defaultPrompt = "",
}: PromptEditorProps) {
  const [prompt, setPrompt] = useState(defaultPrompt);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      onExecute(prompt);
    }
  };

  const handleClear = () => {
    setPrompt("");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex items-center justify-between">
        <Label htmlFor="agent-prompt" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-primary" /> Prompt Task Input
        </Label>
        <span className="text-[11px] font-mono text-muted-foreground">
          {prompt.length} chars
        </span>
      </div>

      <textarea
        id="agent-prompt"
        rows={5}
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter specific instructions or requirements for this agent (e.g., 'Analyze security constraints for a healthcare API...')"
        disabled={isExecuting}
        className="flex w-full rounded-xl border border-input bg-card px-3.5 py-2.5 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 font-sans"
      />

      <div className="flex items-center justify-end gap-2 pt-1">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleClear}
          disabled={isExecuting || !prompt}
        >
          <RotateCcw className="mr-1.5 h-3.5 w-3.5" /> Clear
        </Button>

        <Button type="submit" size="sm" disabled={isExecuting || !prompt.trim()}>
          {isExecuting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Executing Agent...
            </>
          ) : (
            <>
              <Play className="mr-1.5 h-3.5 w-3.5" /> Execute Agent
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
