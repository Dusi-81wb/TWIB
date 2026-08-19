"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { BrainCircuit, User, Zap, Cpu, Clock, Copy, Check, Sparkles } from "lucide-react";
import { MarkdownRenderer } from "./markdown-renderer";
import { Button } from "@/components/ui/button";

export interface ChatTurn {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  provider?: string;
  model?: string;
  latencyMs?: number;
  tokens?: { prompt_tokens: number; completion_tokens: number; total_tokens: number };
}

interface MessageBubbleProps {
  turn: ChatTurn;
  isLast?: boolean;
}

export function MessageBubble({ turn, isLast }: MessageBubbleProps) {
  const bubbleRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (bubbleRef.current) {
      gsap.fromTo(
        bubbleRef.current,
        { opacity: 0, y: 16, scale: 0.96, filter: "blur(4px)" },
        { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.55, ease: "cubic-bezier(0.16, 1, 0.3, 1)" }
      );
    }
  }, [turn.id]);

  const handleCopyAll = () => {
    navigator.clipboard.writeText(turn.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isUser = turn.role === "user";

  return (
    <div
      ref={bubbleRef}
      className={`group flex items-start gap-3.5 my-5 w-full ${
        isUser ? "flex-row-reverse" : "flex-row"
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex h-9 w-9 shrink-0 select-none items-center justify-center rounded-2xl font-bold shadow-md transition-transform duration-200 group-hover:scale-105 ${
          isUser
            ? "bg-gradient-to-tr from-primary to-blue-500 text-white shadow-primary/20"
            : "border border-primary/40 bg-gradient-to-tr from-primary/20 via-purple-500/10 to-transparent text-primary shadow-lg shadow-primary/10"
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <BrainCircuit className="h-4 w-4" />}
      </div>

      {/* Bubble Container */}
      <div
        className={`flex flex-col min-w-0 max-w-[88%] sm:max-w-[82%] space-y-1.5 ${
          isUser ? "items-end" : "items-start"
        }`}
      >
        {/* Role Name & Meta Bar */}
        <div className="flex items-center gap-2 text-[11px] font-mono text-muted-foreground px-1">
          <span className="font-bold text-foreground">
            {isUser ? "You" : "Autonomous Research Agent"}
          </span>
          {turn.timestamp && <span>• {turn.timestamp}</span>}

          {!isUser && (
            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              {turn.provider && (
                <span className="flex items-center gap-0.5 text-primary">
                  <Zap className="h-3 w-3" /> {turn.provider}
                </span>
              )}
              {turn.model && (
                <span className="flex items-center gap-0.5 text-emerald-400">
                  <Cpu className="h-3 w-3" /> {turn.model}
                </span>
              )}
              {turn.latencyMs !== undefined && (
                <span className="flex items-center gap-0.5 text-amber-400">
                  <Clock className="h-3 w-3" /> {turn.latencyMs}ms
                </span>
              )}
            </div>
          )}
        </div>

        {/* Content Box */}
        <div
          className={`relative rounded-3xl px-5 py-4 shadow-md transition-all duration-200 ${
            isUser
              ? "bg-gradient-to-r from-primary to-blue-600 text-white rounded-tr-none font-sans text-sm leading-relaxed"
              : "glass-panel border border-white/10 text-card-foreground rounded-tl-none w-full hover:border-primary/30 hover:shadow-lg"
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap text-sm">{turn.content}</p>
          ) : (
            <MarkdownRenderer content={turn.content} />
          )}

          {/* Copy Button for Assistant turn */}
          {!isUser && (
            <div className="mt-4 pt-3 border-t border-border/40 flex items-center justify-between text-[11px] text-muted-foreground font-mono">
              <div className="flex items-center gap-3">
                {turn.tokens && (
                  <span className="bg-accent/40 px-2 py-0.5 rounded-full border border-border/40">
                    Tokens: {turn.tokens.prompt_tokens} in / {turn.tokens.completion_tokens} out /{" "}
                    <strong className="text-foreground font-bold">{turn.tokens.total_tokens}</strong>
                  </span>
                )}
              </div>

              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopyAll}
                className="h-6 px-2.5 text-[11px] gap-1 hover:bg-accent text-muted-foreground hover:text-foreground rounded-lg"
              >
                {copied ? (
                  <>
                    <Check className="h-3 w-3 text-emerald-400" />
                    <span className="text-emerald-400 font-semibold">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3" />
                    <span>Copy Answer</span>
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
