"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { BrainCircuit, User, Zap, Cpu, Clock, Copy, Check } from "lucide-react";
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
        { opacity: 0, y: 12 },
        { opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }
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
      className={`group flex items-start gap-3 my-4 w-full ${
        isUser ? "flex-row-reverse" : "flex-row"
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-xl font-bold shadow-sm ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "border border-primary/40 bg-primary/10 text-primary"
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <BrainCircuit className="h-4 w-4" />}
      </div>

      {/* Bubble Container */}
      <div
        className={`flex flex-col min-w-0 max-w-[85%] sm:max-w-[80%] space-y-1.5 ${
          isUser ? "items-end" : "items-start"
        }`}
      >
        {/* Role Name & Meta Bar */}
        <div className="flex items-center gap-2 text-[11px] font-mono text-muted-foreground px-1">
          <span className="font-semibold text-foreground">
            {isUser ? "You" : "Research Agent"}
          </span>
          {turn.timestamp && <span>• {turn.timestamp}</span>}

          {!isUser && (
            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
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
          className={`relative rounded-2xl px-4 py-3 shadow-sm ${
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-none font-sans text-sm leading-relaxed"
              : "border border-border/80 bg-card/60 text-card-foreground rounded-tl-none w-full"
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{turn.content}</p>
          ) : (
            <MarkdownRenderer content={turn.content} />
          )}

          {/* Copy Button for Assistant turn */}
          {!isUser && (
            <div className="mt-3 pt-2 border-t border-border/40 flex items-center justify-between text-[11px] text-muted-foreground font-mono">
              <div className="flex items-center gap-3">
                {turn.tokens && (
                  <span>
                    Tokens: {turn.tokens.prompt_tokens} / {turn.tokens.completion_tokens} /{" "}
                    <strong className="text-foreground">{turn.tokens.total_tokens}</strong>
                  </span>
                )}
              </div>

              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopyAll}
                className="h-6 px-2 text-[11px] gap-1 hover:bg-accent text-muted-foreground hover:text-foreground"
              >
                {copied ? (
                  <>
                    <Check className="h-3 w-3 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
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
