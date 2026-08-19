"use client";

import { useState, useRef, useEffect } from "react";
import {
  Send,
  Square,
  SlidersHorizontal,
  Trash2,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

interface ComposerProps {
  onSend: (params: {
    prompt: string;
    model: string;
    temperature: number;
    systemPrompt?: string;
  }) => void;
  isLoading: boolean;
  onStop?: () => void;
  onClear?: () => void;
  defaultModel?: string;
  defaultTemperature?: number;
}

export function Composer({
  onSend,
  isLoading,
  onStop,
  onClear,
  defaultModel = "best-fast",
  defaultTemperature = 0.3,
}: ComposerProps) {
  const [prompt, setPrompt] = useState("");
  const [model, setModel] = useState(defaultModel);
  const [temperature, setTemperature] = useState(defaultTemperature);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [showSettings, setShowSettings] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-grow textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [prompt]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!prompt.trim() || isLoading) return;

    onSend({
      prompt: prompt.trim(),
      model,
      temperature,
      systemPrompt: systemPrompt.trim() || undefined,
    });

    setPrompt("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full border-t border-border/60 bg-background/90 backdrop-blur-md p-3 sm:p-4 space-y-3 select-none">
      {/* Collapsible Advanced Settings Panel */}
      {showSettings && (
        <div className="p-4 rounded-2xl border border-border/80 bg-card/60 shadow-lg space-y-4 text-xs font-mono animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="flex items-center justify-between border-b border-border/40 pb-2">
            <span className="font-bold text-foreground flex items-center gap-1.5 text-xs">
              <SlidersHorizontal className="h-3.5 w-3.5 text-primary" /> Advanced Gateway Settings
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSettings(false)}
              className="h-6 px-2 text-[11px]"
            >
              Close
            </Button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Target Model Selector */}
            <div className="space-y-1.5">
              <Label className="text-[11px] font-semibold flex items-center justify-between">
                <span>Target Model</span>
                <span className="text-[10px] text-muted-foreground">OmniRoute Router</span>
              </Label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full rounded-xl border border-border/80 bg-accent/40 p-2 text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                <option value="best-fast">best-fast (Recommended - Fast & Reliable)</option>
                <option value="best-free">best-free (OmniRoute Free Tier Router)</option>
                <option value="best-coding">best-coding (Claude Sonnet 4.6 Coding)</option>
                <option value="gpt-4o">gpt-4o (OpenAI Flagship)</option>
                <option value="gpt-4o-mini">gpt-4o-mini (OpenAI Fast)</option>
                <option value="llama3">llama3 (Meta Open-Source)</option>
                <option value="claude-3-5-sonnet">claude-3-5-sonnet (Anthropic Sonnet)</option>
              </select>
            </div>

            {/* Temperature Slider */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-[11px] font-semibold">
                <Label>Temperature</Label>
                <span className="font-mono text-primary bg-primary/10 px-1.5 py-0.5 rounded text-[10px]">
                  {temperature.toFixed(2)}
                </span>
              </div>
              <input
                type="range"
                min="0.0"
                max="2.0"
                step="0.05"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full accent-primary cursor-pointer h-1.5 bg-accent rounded-lg"
              />
              <div className="flex justify-between text-[9px] text-muted-foreground font-mono">
                <span>0.0 (Deterministic)</span>
                <span>1.0 (Balanced)</span>
                <span>2.0 (Creative)</span>
              </div>
            </div>
          </div>

          {/* System Prompt Override */}
          <div className="space-y-1.5">
            <Label className="text-[11px] font-semibold">Custom System Prompt Override (Optional)</Label>
            <input
              type="text"
              placeholder="e.g. You are a senior distributed systems architect..."
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              className="w-full rounded-xl border border-border/80 bg-accent/40 p-2 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
        </div>
      )}

      {/* Main Composer Pill Box */}
      <form
        onSubmit={handleSubmit}
        className="relative flex flex-col rounded-2xl border border-border/80 bg-card/70 shadow-lg focus-within:border-primary/60 focus-within:ring-2 focus-within:ring-primary/20 transition-all"
      >
        <textarea
          ref={textareaRef}
          rows={1}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="What would you like the Research Agent to investigate?"
          disabled={isLoading}
          className="w-full resize-none bg-transparent px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none disabled:opacity-50 max-h-[200px]"
        />

        {/* Toolbar & Action Buttons */}
        <div className="flex items-center justify-between px-3 py-2 border-t border-border/40 bg-accent/10">
          <div className="flex items-center gap-1.5">
            {/* Toggle Settings Button */}
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
              className={`h-7 px-2 text-xs gap-1 font-mono ${
                showSettings ? "bg-primary/10 text-primary" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <SlidersHorizontal className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Settings</span>
              {showSettings ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </Button>

            {/* Model Badge Button */}
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full flex items-center gap-1">
              <Zap className="h-2.5 w-2.5" /> {model}
            </span>

            {onClear && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={onClear}
                className="h-7 px-2 text-xs gap-1 text-muted-foreground hover:text-destructive hidden sm:flex"
                title="Clear conversation turns"
              >
                <Trash2 className="h-3.5 w-3.5" /> Clear
              </Button>
            )}
          </div>

          {/* Send / Stop Button */}
          <div className="flex items-center gap-2">
            {isLoading ? (
              <Button
                type="button"
                variant="destructive"
                size="sm"
                onClick={onStop}
                className="h-8 px-3 text-xs gap-1.5 rounded-xl font-bold shadow-sm"
              >
                <Square className="h-3.5 w-3.5 fill-current" /> Stop
              </Button>
            ) : (
              <Button
                type="submit"
                disabled={!prompt.trim()}
                size="sm"
                className="h-8 px-3.5 text-xs gap-1.5 rounded-xl font-bold shadow-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40"
              >
                <span>Send</span>
                <Send className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}
