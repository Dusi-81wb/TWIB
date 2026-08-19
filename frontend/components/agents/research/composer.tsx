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
  Cpu,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { useQuery } from "@tanstack/react-query";
import { settingsService } from "@/services/settings.service";
import { cn } from "@/lib/utils";

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
  defaultModel = "best-free",
  defaultTemperature = 0.3,
}: ComposerProps) {
  const [prompt, setPrompt] = useState("");
  const [model, setModel] = useState(defaultModel);
  const [customModel, setCustomModel] = useState("");
  const [temperature, setTemperature] = useState(defaultTemperature);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [showSettings, setShowSettings] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { data: models = [] } = useQuery({
    queryKey: ["omniroute-models"],
    queryFn: () => settingsService.getOmniRouteModels(),
  });

  const { data: config } = useQuery({
    queryKey: ["omniroute-config"],
    queryFn: () => settingsService.getOmniRouteConfig(),
  });

  useEffect(() => {
    if (config?.default_model) {
      setModel(config.default_model);
    }
  }, [config]);

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

    const activeModel = customModel.trim() || model;
    onSend({
      prompt: prompt.trim(),
      model: activeModel,
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

  const activeModelDisplay = customModel.trim() || model;

  return (
    <div className="w-full border-t border-white/10 bg-background/90 backdrop-blur-xl p-3 sm:p-4 space-y-3 select-none">
      {/* Collapsible Advanced Settings Panel */}
      {showSettings && (
        <div className="p-4 rounded-3xl border border-white/10 bg-card/80 shadow-2xl space-y-4 text-xs font-mono animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="flex items-center justify-between border-b border-border/40 pb-2">
            <span className="font-bold text-foreground flex items-center gap-1.5 text-xs">
              <SlidersHorizontal className="h-3.5 w-3.5 text-primary" /> Live Gateway & Model Strategy
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
            {/* Live Model Selection */}
            <div className="space-y-1.5">
              <Label className="text-[11px] font-semibold flex items-center justify-between">
                <span>Active Model</span>
                <span className="text-[10px] text-emerald-400 font-mono">Live Endpoint</span>
              </Label>
              <div className="grid grid-cols-2 gap-1.5 max-h-36 overflow-y-auto pr-1">
                {models.map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => {
                      setModel(m);
                      setCustomModel("");
                    }}
                    className={cn(
                      "p-2 rounded-xl border text-left text-[11px] font-mono truncate transition-all",
                      model === m && !customModel
                        ? "border-primary bg-primary/10 text-primary ring-1 ring-primary"
                        : "border-border/60 bg-background/60 hover:border-border text-foreground"
                    )}
                  >
                    {m}
                  </button>
                ))}
              </div>
              <Input
                value={customModel}
                onChange={(e) => setCustomModel(e.target.value)}
                placeholder="Or custom model ID..."
                className="h-8 text-xs font-mono bg-background/70 mt-1"
              />
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
                max="1.5"
                step="0.05"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full accent-primary cursor-pointer h-1.5 bg-accent rounded-lg"
              />
              <div className="flex justify-between text-[9px] text-muted-foreground font-mono">
                <span>0.0 (Deterministic)</span>
                <span>0.7 (Balanced)</span>
                <span>1.5 (Creative)</span>
              </div>
            </div>
          </div>

          {/* System Prompt Override */}
          <div className="space-y-1.5">
            <Label className="text-[11px] font-semibold">System Instructions Override (Optional)</Label>
            <Input
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="e.g., 'You are an autonomous research intelligence specialist. Provide exhaustive citations.'"
              className="font-sans text-xs bg-background/60 h-8"
            />
          </div>
        </div>
      )}

      {/* Main Composer Bar */}
      <div className="relative rounded-3xl border border-white/10 bg-card/70 shadow-lg focus-within:border-primary/50 focus-within:ring-2 focus-within:ring-primary/20 transition-all">
        <textarea
          ref={textareaRef}
          rows={1}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Research Agent to synthesize market trends, API documentation, or technical analysis..."
          disabled={isLoading}
          className="w-full resize-none bg-transparent px-4 pt-3.5 pb-12 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none disabled:opacity-50 font-sans leading-relaxed"
        />

        {/* Bottom Toolbar inside Composer */}
        <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between pointer-events-auto">
          <div className="flex items-center gap-2">
            {/* Model Badge button that opens settings */}
            <button
              type="button"
              onClick={() => setShowSettings(!showSettings)}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-accent/40 hover:bg-accent/70 border border-white/5 text-[11px] font-mono text-muted-foreground hover:text-foreground transition-all cursor-pointer"
            >
              <Cpu className="h-3 w-3 text-emerald-400" />
              <span className="truncate max-w-[130px] sm:max-w-[200px]">{activeModelDisplay}</span>
              {showSettings ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </button>

            {onClear && (
              <button
                type="button"
                onClick={onClear}
                disabled={isLoading}
                className="p-1 rounded-lg text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10 transition-colors disabled:opacity-40"
                title="Clear Chat Conversation"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            )}
          </div>

          <div className="flex items-center gap-2">
            {isLoading && onStop ? (
              <Button
                type="button"
                size="sm"
                variant="destructive"
                onClick={onStop}
                className="h-8 px-3 rounded-xl gap-1.5 text-xs font-semibold"
              >
                <Square className="h-3 w-3 fill-current" /> Stop
              </Button>
            ) : (
              <Button
                type="button"
                size="sm"
                onClick={() => handleSubmit()}
                disabled={!prompt.trim() || isLoading}
                className="h-8 px-3.5 rounded-2xl bg-primary hover:bg-primary/90 text-white shadow-md shadow-primary/25 gap-1.5 text-xs font-semibold transition-all disabled:opacity-40"
              >
                <span>Send</span>
                <Send className="h-3 w-3" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
